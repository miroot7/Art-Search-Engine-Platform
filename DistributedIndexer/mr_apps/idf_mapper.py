#!/usr/bin/env python3

#The mapper's job is to associate each term with every document ID that it appears in.  
#outputs key-value pairs of the form (term, doc_id). 

import sys
import nltk
import json
#nltk.download('punkt')
#nltk.download('corpora')
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from collections import Counter
import string
from nltk.stem.snowball import SnowballStemmer
import re

for line in sys.stdin:
	page = json.loads(line)
	text = str(page["docText"].lower())
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
	
	words = textwords + titlewords
	stemmer = SnowballStemmer("english")
	words = [word.strip('{}()#|') for word in words if len(word)<30]
	words = [stemmer.stem(word) for word in words ]
	stop_words = set(stopwords.words('english'))
	stop_words_file = open('DistributedIndexer/criteria/stopwordsList')
	stop_words_list = stop_words_file.read().splitlines()
	for w in stop_words_list:
		stop_words.add(w)
	words_filtered = []
	for w in words:
		if w not in stop_words:
			words_filtered.append(w)

	for word in set(words):
		print("%s\t%s" % (word, page["docID"]))
