import sys
import os

def get_response(num_sents):
    results = []
    print ('\n')
    response = int( input('ENTER sentence number: ') )
    responces = 0
    while int(response) != 0 :
        index = response-1
        if index in results:
            print ("Notice: You have already selected sentence number: " + str(response) + " please select another sentence.")
        else:    
            results.append( index )
            responces = responces + 1
        
        if responces > 4 or responces >= num_sents:
            break
        
        response  = int ( input('ENTER sentence number: ') )
        
    print ("\n")
    return results

#if continuing from previous times
def get_previous_results():
    print("Getting previous results . . . ")
    results = set([])
    if os.path.exists('m_positive_annotations.txt'):
        with open ('m_positive_annotations.txt', 'r') as f:
            for line in f.readlines():
                item = line.split('\t')
                results.add(item[0])
    
    if os.path.exists('m_negative_annotations.txt'):
        with open ('m_negative_annotations.txt', 'r') as f:
            for line in f.readlines():
                item = line.split('\t')
                results.add(item[0])        
    
    return results

def main(args):    
    #papers_done = []
    #if len(args) > 0:
    papers_done = list(get_previous_results())
    num_papers_done = len(papers_done)
    annotation_data = []
    with open('MachineTranslation_annotation_file.txt', 'r') as f:
        annotation_data = f.readlines()
    print ("number of papers done:", len(papers_done)) 
    paperIds2Sents = {}
    print( "Which of the following are most descriptive of future work (if any). Vote at most 5." )
    for line in annotation_data:
        #if (num_papers_done > 30):
        #    break
        #num_papers_done = num_papers_done + 1
        item = line.split('\t')
        paperID = item[0]
        title = item[1]
        query = item[2]
        
        #if this paperID has already been tag.
        if paperID in papers_done:
            continue
        
        if paperID not in paperIds2Sents:
            paperIds2Sents[paperID] = {}
            paperIds2Sents[paperID]['sents'] = []
        
        paperIds2Sents[paperID]['title'] = title
        paperIds2Sents[paperID]['sents'].append(query)

    print ("papers left:", len(paperIds2Sents))
    for paperID in paperIds2Sents:
        print ("INSTRUCTIONS: You are given the title of the article followed by several sentences. Select the most relevent to future works. If none of the remaining sentences are relevant type 0.\n")
        print ("TITLE: " + paperIds2Sents[paperID]['title'] )
        for i, query in enumerate(paperIds2Sents[paperID]['sents']):
            print ( str(i+1) + ": " + query)
        results = get_response(i+1)

        positive_results = []
        negative_results = []
        for i, query in enumerate(paperIds2Sents[paperID]['sents']):
            if i in results:
                positive_results.append(paperID + "\t" + query)
            else:
                negative_results.append(paperID + "\t" + query)

        if len(positive_results) > 0:
            with open ('m_positive_annotations.txt', 'a+') as f:
                f.writelines( positive_results ) 

        if len(negative_results) > 0:
            with open ('m_negative_annotations.txt', 'a+') as f:
                f.writelines( negative_results)

if __name__=="__main__":
    main(sys.argv [1:])
