from bs4 import BeautifulSoup
from bs4 import BeautifulStoneSoup
import nltk.data
import re
import glob
import pickle
import pprint

sent_detector = nltk.data.load('tokenizers/punkt/english.pickle')
FW_ABS_Index = {}
def main():
    output_pickle = 'FutureWorkAndAbstractPickle_v2.pk'
    input_directory = "../cleanXMLdataV2/*.out"
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

            if header['genericHeader'] == 'conclusions' and float( header['confidence']) > 0.95:
                #print "1:" + header.find_next('bodyText').get_text()
                if header.find_next('bodyText') is not None:
                    #print "2:" + header.find_next('bodyText').get_text()
                    paperCon = get_abstract(header.find_next('bodyText').get_text())
                else:
                    paperCon = " "
                    FW_ABS_Index[paperId][3] = paperCon
                    print "paperCon: " + FW_ABS_Index[paperId][3]
                
            if header['genericHeader'] == 'conclusions':
                if float( header['confidence']) < 0.95:
                    bodiesCON = header.find_all_previous('bodyText', limit=3)
                bodiesCON = bodiesCON +  header.find_all_next('bodyText')	
        
        bodyConText = ""
        for item in bodiesCON:
            bodyConText += item.get_text()

        futureWorkText = get_futureWork(bodyConText)
        FW_ABS_Index[paperId][1] = futureWorkText

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
        saveText = starterPointer.get_text()
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
    return saveText

if __name__=="__main__":
    main()




