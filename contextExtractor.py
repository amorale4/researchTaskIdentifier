import re

#assuming we are running the python script at the location where aan is located
def main():
	metaPath="aan/release/"
	dataPath="aan/papers_text/"
	year="2013"
	paper_id = "N10-1034.txt"
	
	paper = ""
	with open(dataPath+paper_id) as dp:
		paper = dp.read()

	#citations = re.findall(r"([(]([^,|^)]+[,]\s\d+;*\s*)+[)])", paper)
	window = 100; #100 character window
	citation_context = []
	for m in re.finditer(r"([(]([^,|^)|^(]+[,]\s\d+;*\s*)+[)])", paper):
		print '%02d-%02d: %s' % (m.start(), m.end(), m.group(0))
		context = paper[(m.start()-window):(m.end()+100)]
		print context + "\n"
		citation_context.append(context)
	
	#print len(citations)
	#print citations	
	#print citation_context[0]
	return

def findCitations():
	
	return

if __name__ == "__main__":
	main()
