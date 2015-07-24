from bs4 import BeautifulSoup
from bs4 import BeautifulStoneSoup
import nltk.data
import re
import glob
import pickle
import pprint
from nltk.tokenize import word_tokenize
from nltk.stem.porter import PorterStemmer

sent_detector = nltk.data.load('tokenizers/punkt/english.pickle')
stopwords = nltk.corpus.stopwords.words('english')+[',','.','!','``',"''",'?',"'s",';','$',':',"'",'_', ')', '(']
stemmer = PorterStemmer()

FW_ABS_Index = {}
def main():
    #basic
    #indicators = ['futur', 'plan']
    #expanded
    indicators = ['futur', 'work', 'plan', 'improv', 'explor', 'approach', 'perform', 'research', 'evalu', 'extend', 'would']
    output_pickle = 'FutureWorkAndAbstractPickle_expanded.pk'
    #output_pickle = 'temp'
    input_directory = "../cleanXMLdataV2/*.out"
    #input_directory = "../cleanXMLdataV2/P11-2088.out"
    #read_files = glob.glob("/Users/aditi_khullar/Documents/Dropbox/cleanXMLdataV2/*.out")
    read_files = glob.glob(input_directory)
    for xmlFile in read_files:
        paperId = xmlFile.split("/")[-1][0:-4]
        print paperId
        if FW_ABS_Index.has_key(paperId) is False:
            FW_ABS_Index[paperId] = ["Smaple Abstract", "Sample Futurework", "Sample Intro", "Sample Con"]
        with open(xmlFile, 'r') as f:
            xmlData = f.read();
        #`soup = BeautifulStoneSoup(xmlData, selfClosingTags=['sectionHeader','bodyText'])
        soup = BeautifulSoup(xmlData, 'xml')
        #print soup.prettify()

        bodiesAWK = []
        # gets all of the lines after conclusion and before acknowledgement
        limit = 5 #assuming that there are not many seperations between conclusion and acknowledgement
        bodiesCON = []
        
        bodyConText = ""
        for i, header in  enumerate(soup.findAll('sectionHeader')):
            #print i
            if header['genericHeader'] == 'abstract':    
                if header.find_next('bodyText') is not None:
                    paperAbs = get_abstract(header.find_next('bodyText').get_text())
                else:
                    paperAbs = " "
                FW_ABS_Index[paperId][0] = paperAbs
               
            if header['genericHeader'] == 'introduction':
                #startPointer = header.find_next('bodyText')
                #print "1:" + header.find_next('bodyText').get_text()
                #if header.find_next('bodyText') is not None:
                #    #print "2:" + header.find_next('bodyText').get_text()
                #    paperIntro = get_abstract(header.find_next('bodyText').get_text())
                #else:
                #    #paperIntro = " "
                FW_ABS_Index[paperId][2] = get_abstract(get_bodyText(header))
                #print FW_ABS_Index[paperId][2]
            
            #gets the conclusion section
            if header['genericHeader'] == 'conclusions' and float( header['confidence']) > 0.95:
                #print "1:" + header.find_next('bodyText').get_text()
                if header.find_next('bodyText') is not None:
                    #print "2:" + header.find_next('bodyText').get_text()
                    paperCon = get_abstract(header.find_next('bodyText').get_text())
                else:
                    paperCon = " "
                
                FW_ABS_Index[paperId][3] = paperCon
                #print "paperCon: " + FW_ABS_Index[paperId][3]
                
            #gets all of what we believe is the conclusion section to extract future works in
            if header['genericHeader'] == 'conclusions':
                if float( header['confidence']) < 0.95:
                    #bodiesCON = header.find_all_previous('bodyText', limit=3)
                    #print header['confidence']
                    bodyConText = get_abstract(prev_bodyText(header))
                else:
                    #print 'bodies'
                    #print header
                    #print header.find_next()
                    bodyConText = get_abstract(get_bodyText(header))#bodiesCON +  header.find_all_next('bodyText')

        #bodyConText = ""        
        #for item in bodiesCON:
        #    bodyConText += item.get_text()

        #print bodyConText
        #print "-----------------"
        
        futureWorkText = get_futureWork_extended(bodyConText,indicators)
        FW_ABS_Index[paperId][1] = futureWorkText
        
        #print futureWorkText
        
    #bodiesCON =  header.find_next('bodyText').find_next('bodyText')
    # print len(FW_ABS_Index)
    # print "Abstract"
    # print FW_ABS_Index['W10-4150'][0]
    # print "Future Work"
    # print FW_ABS_Index['W10-4150'][1]
    
    # Writing the Dictinary to a file
    # fileW = open("FutureWorkAndAbstractIndex.txt", "w")
    # for key in FW_ABS_Index:
    #     values = ""
    #     print FW_ABS_Index[key]
    #     for v in FW_ABS_Index[key]:
    #         values = values + " \n----\n " + v
    #     fileW.write("%s : %s\n" % (key, values)) 


    # Writing the Dictinary to a pickle file
    output = open(output_pickle, 'wb')
    pickle.dump(FW_ABS_Index, output)
    output.close()

    return

def get_futureWork(all_text):
    ret = ""
    pattern = re.compile("future")	
    for sent in sent_detector.tokenize(all_text.strip()):
        clean_sent = sent.lower().replace('\n', ' ').strip()
        clean_sent = clean_sent.replace("- ", "")
        if pattern.search(clean_sent):
            ret = ret + "\n" + clean_sent

    return ret

def get_futureWork_plus(all_text):
    ret = ""
    pattern1 = re.compile("future")
    pattern2 = re.compile("plan to")
    for sent in sent_detector.tokenize(all_text.strip()):
        clean_sent = sent.lower().replace('\n', ' ').strip()
        clean_sent = clean_sent.replace("- ", "")
        if pattern1.search(clean_sent):
            ret = ret + "\n" + clean_sent
        
        #todo make sure the sentence is not added already
        elif pattern2.search(clean_sent):
            ret = ret + "\n" + clean_sent
            
    return ret

def get_futureWork_extended(all_text, indicators):
    ret = ""
    #indicators = ['futur', 'work', 'use', 'plan', 'model', 'improv', 'system', 'research', 'method', 'featur', 'includ', 'investig', 'explor', 'direct', 'languag', 'would', 'data', 'evalu', 'approach', 'perform']
    #indicators = ['futur', 'work', 'plan', 'improv', 'explor', 'approach', 'perform', 'research', 'evalu', 'extend', 'would']
    for sent in sent_detector.tokenize(all_text.strip()):
        clean_sent = sent.lower().replace('\n', ' ').strip()
        clean_sent = clean_sent.replace("- ", "")
        
        for token in [t.lower() for t in nltk.word_tokenize(clean_sent)]:
            if token in stopwords:
                continue
            if stemmer:
                token = stemmer.stem(token)
            
            if token in indicators:
                ret = ret + "\n" + clean_sent
                break
            
    return ret

def get_abstract(all_text):
    ret = ""
    for sent in sent_detector.tokenize(all_text.strip()):
        clean_sent = sent.lower().replace('\n', ' ').strip()
        clean_sent = clean_sent.replace("- ", "")
        ret = ret + "\n" + clean_sent

    return ret

def get_bodyText(starterPointer):
    saveText = " "
    if starterPointer is not None:
        #saveText = starterPointer.get_text()
        currentPoint = starterPointer.find_next()
        while currentPoint is not None :
            #print currentPoint.name
            if currentPoint.name == 'sectionHeader':
                break
            #elif currentPoint.name == 'page':
            #    print currentPoint.name
            elif currentPoint.name == 'bodyText':
                saveText = saveText + currentPoint.get_text()

            currentPoint = currentPoint.find_next()
            
    #print saveText
    return saveText

def prev_bodyText(starterPointer):
    saveText = " "
    if starterPointer is not None:
        saveText = starterPointer.get_text()
        currentPoint = starterPointer.find_previous()
        while currentPoint is not None :
            #print currentPoint.name
            if currentPoint.name == 'sectionHeader':
                break
            #elif currentPoint.name == 'page':
            #    print currentPoint.name
            elif currentPoint.name == 'bodyText':
                saveText = saveText + currentPoint.get_text()

            currentPoint = currentPoint.find_previous()
    return saveText


if __name__=="__main__":
    main()




