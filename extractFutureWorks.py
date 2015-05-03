from bs4 import BeautifulSoup
from bs4 import BeautifulStoneSoup
import nltk.data
import re

sent_detector = nltk.data.load('tokenizers/punkt/english.pickle')
def main():
	xmlFile="cleanXMLdataV2/W11-0707.out"
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

		if header['genericHeader'] == 'conclusions':
			if float( header['confidence']) < 0.95:
				bodiesCON = header.find_all_previous('bodyText', limit=3)
			bodiesCON = bodiesCON +  header.find_all_next('bodyText')
			#print bodiesCON
			#print bodiesCON
	
		#if header['genericHeader'] == 'acknowledgments':
		#	bodiesAWK = header.find_all_previous('bodyText', limit=limit)
			
	bodyConText = ""
	
	for item in bodiesCON:
		bodyConText += item.get_text()
		
	#for awkbody in reversed(bodiesAWK):
	#	if awkbody in bodiesCON:
	#		bodyConText += awkbody.get_text()

	#print "context: " + bodyConText
	print get_futureWork(bodyConText)
	#bodiesCON =  header.find_next('bodyText').find_next('bodyText')
		
def get_futureWork(all_text):
	ret = ""

	#for body in textBodies:
	#	all_text += body.get_text()
		
	#print all_text
	pattern = re.compile("future")	
	for sent in sent_detector.tokenize(all_text.strip()):
		clean_sent = sent.lower().replace('\n', ' ').strip()
		clean_sent = clean_sent.replace("- ", "")
		#print clean_sent
		#print "------------------"
		if pattern.search(clean_sent):
			print ' >>> there was a match <<< '
			ret += sent
			print clean_sent
			print 

	return ret


if __name__=="__main__":

	main();




