from bs4 import BeautifulSoup
from bs4 import BeautifulStoneSoup

def main():
	xmlFile="cleanXMLdataV2/W11-0706.out"
	with open(xmlFile, 'r') as f:
		xmlData = f.read();
	#soup = BeautifulStoneSoup(xmlData, selfClosingTags=['sectionHeader','bodyText'])
	soup = BeautifulSoup(xmlData, 'xml')
	#print soup.prettify()
	#bodies = soup.findAll('bodyText')
	for i, header in  enumerate(soup.findAll('sectionHeader')):
		#print header
		if header['genericHeader'] == 'conclusions':
			bodiesCON =  header.find_all_next('bodyText')
			get_futureWork(bodiesCON[0])
			
		
def get_futureWork(text):
	ret = ""
	print text
	
	return ret


if __name__=="__main__":

	main();
