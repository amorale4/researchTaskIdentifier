import nltk
from collections import defaultdict
from nltk.stem.porter import PorterStemmer
from nltk.tokenize import RegexpTokenizer
from math import *
import pickle
import os
import re
import numpy as np
from math import log
import operator

class Index:
 
	def __init__(self, tokenizer, stemmer=None, stopwords=None):
		self.tokenizer = tokenizer
		self.stemmer = stemmer
		self.index = defaultdict(list)
		self.collectionindex = defaultdict(int)
		self.numberofwords = 0 # Total number of words in the whole collection C
		self.docnumberofwords = defaultdict(int) # Dictionary of the number of (stemmed) words in each document
		self.DocCollection = defaultdict(list) # Dictionary of all documents - Forward Index
		self.numberofdocuments = 0

		if not stopwords:
			self.stopwords = set()
		else:
			self.stopwords = set(stopwords)
 
	def search(self, word): 
		return [documentID for documentID in self.index[word]]
 
	def stem(self,Q):
		Qnew = []
		for token in [t.lower() for t in nltk.word_tokenize(Q)]:
			if token in self.stopwords:
				continue
			token = self.stemmer.stem(token)
			Qnew.append(token)
		return Qnew
			

	def PCollection(self):
		for word in self.index:
			sumword = 0
			for documentID in self.index[word]:
				sumword = sumword + self.index[word][documentID]
			self.collectionindex[word] = sumword/(self.numberofwords)
				

	def add(self, document, documentID):
		self.numberofdocuments += 1
		for token in [t.lower() for t in nltk.word_tokenize(document)]:
			if token in self.stopwords:
				continue
 
			if self.stemmer:
				token = self.stemmer.stem(token)
			if documentID not in self.DocCollection:
				self.DocCollection[documentID] = []

			self.DocCollection[documentID].append(token)

			if token not in self.index:
				self.index[token] = defaultdict(int)

			if documentID not in self.index[token]:
				self.index[token][documentID] = 1
			
			else:
				self.index[token][documentID] += 1

			self.numberofwords += 1
			self.docnumberofwords[documentID] += 1



	def addfiles(self):
		D = pickle.load(open('pub_dictionary_final','rb'))
		for documentID in D:
			self.add(D[documentID][0]+' '+D[documentID][5],documentID) # Add the title and the abstract of each document to the index
		self.PCollection()


def Feedback(index,FeedbackDocsIDs,clf,mu,numterms,Lambda): #FeedbackDocsIDs contains the document IDs of "upto" the 10 top documents
	docterms = set() # Set of feedback terms
	DF = defaultdict(int) # Dictionary of normalized DFs
	GM = defaultdict(int) # Dictinary of geometric means
	IDF = defaultdict(int) # Dictionary of IDFs (normalized to include only the feedback terms)
	PWDF = defaultdict(int)
	for documentID in FeedbackDocsIDs:
		document = index.DocCollection[documentID]
		for word in document:
			docterms.add(word)
	
	for documentID in FeedbackDocsIDs:
		document = index.DocCollection[documentID]
		PWDF[documentID] = defaultdict(int)
		for word in document:
			PWDF[documentID][word] += 1

		for word in docterms:
			PWDF[documentID][word] = Smoothing(word,PWDF[documentID][word],index.docnumberofwords[documentID], mu, index,'Feedback',len(docterms))
		
		for word in docterms:
			if word in document:
				DF[word] += 1/len(FeedbackDocsIDs)

	totalcoprob = 0	
	for word in docterms:
		GM[word] = mean([ PWDF[documentID][word] for documentID in FeedbackDocsIDs])
		totalcoprob += index.collectionindex[word]

	for word in docterms:
		IDF[word] = index.collectionindex[word]/totalcoprob
	'''
	total = 0	
	for term in docterms:
		if clf.predict([PWDF[documentID][term] for documentID in FeedbackDocsIDs] + [IDF[term], DF[term], GM[term], GM[term]/IDF[term]]) == 1:
			total += 1
		else:
			print(term)
	print(total/len(docterms), total, len(docterms))
	'''
	newterms = []
	for term in docterms:
		#if clf.predict([PWDF[documentID][term] for documentID in FeedbackDocsIDs] + [IDF[term], DF[term], GM[term], GM[term]/IDF[term]]) == 1:
		newterms.append(term)
	
	for documentID in FeedbackDocsIDs:
		totalprob = 0
		for term in newterms:
			totalprob +=  PWDF[documentID][term]
		for term in newterms:
			PWDF[documentID][term] = PWDF[documentID][term] / totalprob # Renormalizing the probabilities
	totalcoprob = 0
	for term in newterms:
		totalcoprob += IDF[term]

	for term in newterms:
		IDF[term] = IDF[term]/totalcoprob

	# Calculation of the final probabilities starts here - Not efficient  (Old implementation.. but correct)
	PWQNew = defaultdict(int)
	PWQ = defaultdict(int)
	totalprob = 0
	for feedbackterm in newterms:
		#PWQNew[feedbackterm] = (mean([PWDF[documentID][feedbackterm] for documentID in FeedbackDocsIDs])**(1/(1-Lambda)))/((IDF[feedbackterm])**(Lambda/(1-Lambda))) # Original DMM
		PWQNew[feedbackterm] = (mean([PWDF[documentID][feedbackterm] for documentID in FeedbackDocsIDs])**(1+Lambda))/((IDF[feedbackterm])**(Lambda))

	results = sorted(PWQNew.items(), key=lambda x: x[1],reverse = True)
	for i in range(0,min(numterms,len(results))):
		PWQ[results[i][0]]= results[i][1]	
		totalprob += results[i][1]

	for word in PWQ:
		PWQ[word] = PWQ[word]/totalprob
			
	for word,p in sorted(PWQ.items(), key=lambda x: x[1],reverse = True): # For printing the feedback terms
		print(word,p)
	
	return PWQ	

def Retrieve(Q,index,mu,feedback,Lambda,numdocs,numterms,alpha,aggregation='geometric'):
	PWQ = defaultdict(int)
	PWD = defaultdict(int)
	PWDF = defaultdict(int)
	matchingdocs = set()
	RetResults =[]
	if feedback == 0:
		Q = index.stem(Q)
		lenQ = len(Q)
		for q in Q:
			PWQ[q] += 1/lenQ

	elif feedback == 'nofeedback':
		Q = index.stem(Q)
		lenQ = len(Q)
		for q in Q:
			PWQ[q] += 1/lenQ
		feedback = 1

	else:
		PWQ = Q

##########################################################################################
### Update: Now this chunk returns the documents with only intersection(Q,D) as keys
	for q in PWQ:
		for documentID in index.search(q):
			matchingdocs.add(documentID)
	for q in PWQ:
		for documentID in index.search(q):
			if documentID not in PWD:
				PWD[documentID]= defaultdict(int)
			PWD[documentID][q] = Smoothing(q,index.index[q][documentID],index.docnumberofwords[documentID], mu, index,'Retrieval',0)
			#print(q,documentID,PWD[documentID][q])	
############################################################################################

	#print('Feedback= ',feedback)
	for documentID in matchingdocs:
		RetResults.append((documentID,KLDivRetrievalFunction(PWQ,PWD[documentID],index,index.docnumberofwords[documentID],mu)))

	RetResultsSorted = sorted(RetResults, key=lambda tup: tup[1], reverse = True)
	if feedback == 0:
		terms = set()
		docterms = set()
		FeedbackDocsIDs=[]
		for i in range(0,min(len(RetResultsSorted),numdocs)):
			FeedbackDocsIDs.append(RetResultsSorted[i][0])



		for documentID in FeedbackDocsIDs:
			document = index.DocCollection[documentID]
			for word in document:
				docterms.add(word)


		for documentID in FeedbackDocsIDs:
			document = index.DocCollection[documentID]
			PWDF[documentID] = defaultdict(int)
			for word in document:
				PWDF[documentID][word] += 1

			for word in docterms:
				PWDF[documentID][word] = Smoothing(word,PWDF[documentID][word],index.docnumberofwords[documentID], mu, index,'Feedback',len(docterms))

		Q = Feedback(index,FeedbackDocsIDs,clf,mu,numterms,Lambda)
		
		#Q = DivMinFeedback(PWQ,PWDF,index.collectionindex,Lambda,numterms) # TURN THIS ON
		
		for q in Q:
			terms.add(q)
		for q in PWQ:
			terms.add(q)
		for q in terms:
			Q[q] = (1-alpha)*PWQ[q] + alpha*Q[q]
			#print(q,Q[q])
		
		return Retrieve(Q,index,mu,1,Lambda,numdocs,numterms,alpha,clf) # TURN THIS ON
	else:
		return RetResultsSorted[0:1000] # Return the top 1000 documents

def Smoothing(word,count,lenD,mu,index,Mode,NumTerms): # Mode= retrieval or feedback
	#print(word,count,(count+mu*index.collectionindex[word])/(lenD+mu))
	if Mode=='Retrieval':
		return (count+mu*index.collectionindex[word])/(lenD+mu) # Dirichlet Prior Smoothing
		#return (count+0.1)/(lenD+0.1*len(index.collectionindex))
	if Mode=='Feedback':
		#return (count+0.1)/(lenD+0.1*len(index.collectionindex))
		return (count+0.1)/(lenD+0.1*NumTerms)
		#return (count+mu*index.collectionindex[word])/(lenD+mu) # Dirichlet Prior Smoothing
		#return count/lenD
def KLDivRetrievalFunction(PWQ,PWD,index,Dlen,mu):
	score = 0
	for word in PWD: # Since PWD contains the intersection of Q and D
		score = score + PWQ[word]*log((PWD[word]*(Dlen+mu))/(mu*index.collectionindex[word]))
	score = score + log(mu/(mu+Dlen))
	return score
		
def mean(PWD):
	product = 1
	i = 0 # number of docs
	for p in PWD:
		i += 1
		product = product*p
	return product**(1/i)




''' Used only for indexing the dataset (run only once)
index = Index(nltk.word_tokenize, PorterStemmer(), nltk.corpus.stopwords.words('english')+[',','.','!','``',"''",'?',"'s",';','$',':',"'",'_'])
index.addfiles()
pickle.dump(index,open('index','wb'))
'''

f = open('PickleCreation/index','rb')
index = pickle.load(f)
f.close()

query = 'support vector machines'
print(Retrieve(query,index,1000,'nofeedback',0.1,10,50,0.9)[0:100]) # Retrieve will return a ranked list of tuples of the form (documentID, documentScore).

