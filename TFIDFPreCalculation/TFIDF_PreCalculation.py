
import os
import sys
from sklearn import feature_extraction
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
import sys
import nltk
import json
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from collections import Counter
import string
# from google.cloud import storage
import logging
import os
import scipy.sparse
from scipy.sparse import csr_matrix
import pickle
from scipy import io
import re
# Add following to frontend to modify the user entered query.
from nltk.stem.snowball import SnowballStemmer
# Add above to frontend to modify the user entered query.


if __name__ == '__main__':
	#read files
	inputFile = open('TFIDFPreCalculation/tfidf_data/data', 'r') 
	#docIDs = []
	texts = []
	for line in inputFile:
		page = json.loads(line)
		text = str(page["docText"].lower())
		#docIDs.append(page["docID"])
		#print(page["docID"])
		#for l in text:

		text = "".join(l for l in text if l not in string.punctuation)
		title = page["title"].lower()
		title = "".join(l for l in title if l not in string.punctuation)
		text = re.sub(r'\{\{.*?\}\}', '', text, flags=re.S)
		text = re.sub(r'<ref>.*?</ref>', '', text, flags=re.S)
		text = re.sub(r'\[\[File:.*?\|.*?\|.*?\|(.*?)\]\]', r'\1', text, flags=re.S)
		UGLY_TEXT_MAP = dict([(ord(char), None) for char in '[]{}'] + [(ord(char), ' ') for char in '|=*\\#'])
		text = text.translate(UGLY_TEXT_MAP)
		text = text.replace("'''", '"').replace("''", '"')
		text = text.strip()
		textwords = nltk.word_tokenize(text) #List of string
		titlewords = nltk.word_tokenize(title)
		words = textwords + titlewords * 99

		# Add following to frontend to modify the user entered query. Input list of words, output list of words.
		stemmer = SnowballStemmer("english")
		words = [word.strip('{}()#|') for word in words if len(word)<30]
		words = [stemmer.stem(word) for word in words ]
		# Add above to frontend to modify the user entered query.

		stop_words = set(stopwords.words('english'))
		stop_words_file = open('DistributedIndexer/criteria/stopwordsList')
		stop_words_list = stop_words_file.read().splitlines()
		for w in stop_words_list:
			stop_words.add(w)
		words_filtered = []
		for w in words:
			if w not in stop_words:
				words_filtered.append(w)
	
		text_string = " ".join(word for word in words_filtered)
		texts.append(text_string)
	#print(len(words))

	vectorizer = CountVectorizer()
	transformer = TfidfTransformer()
	idf_vectorizer = TfidfVectorizer()
	x = idf_vectorizer.fit_transform(texts)
	idf = idf_vectorizer.idf_
	inverted_index = vectorizer.fit_transform(texts)
	pickle.dump(inverted_index,open('TFIDFPreCalculation/tfidf_data/inverted-index','wb'))
	tfidf = transformer.fit_transform(inverted_index)
	pickle.dump(idf,open('TFIDFPreCalculation/tfidf_data/idf','wb'))
	word = vectorizer.get_feature_names()
	#print(len(word))
	#for i in word:
		#print(i)
	pickle.dump(word,open('TFIDFPreCalculation/tfidf_data/words','wb'))
	#weight = tfidf.toarray() #weight[i][j] j word in i doc's tf-idf
	#io.mmwrite('tf-idf-matrix', tfidf)
	#app = webapp2.WSGIApplication([('/', MainPage)],
                              #debug=True)
	#MainPage.create_file(app,cloudpickle.dump(weight,open('tf-idf-matrix','wb')))
	
	#csr_matrix(weight).toarray()
	pickle.dump(tfidf,open('TFIDFPreCalculation/tfidf_data/tf-idf-matrix','wb'))
	#pickle.dump(docIDs,open('TFIDFPreCalculation/tfidf_data/doc-id-list','wb'))
	#print(len(tfidf))
	#for i in range(len(weight)):
		#print(docIDs[i])
		#for j in range(len(word)):
			#if (weight[i][j]!=0):
				#print (word[j], weight[i][j])


	
