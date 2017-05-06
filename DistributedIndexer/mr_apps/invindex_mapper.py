#!/usr/bin/env python3

#The mapper's job is to associate each document with every term that appears in it, along with that term's frequency.
#input: *.in by the reformatter
#output: (doc_id, (term, tf))
import sys
import nltk
import json
#nltk.download('punkt')
#nltk.download('corpora')
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from collections import Counter
import string
import re
from nltk.stem.snowball import SnowballStemmer


for line in sys.stdin:
	page = json.loads(line)
	text = page["docText"].lower()
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
	stop_words = set(stopwords.words('english'))
	stop_words_file = open('DistributedIndexer/criteria/stopwordsList')
	stop_words_list = stop_words_file.read().splitlines()
	for w in stop_words_list:
		stop_words.add(w)
	
	words = textwords + titlewords * 99
	stemmer = SnowballStemmer("english")
	words = [word.strip('{}()#|') for word in words if len(word)<30]
	words = [stemmer.stem(word) for word in words ]
	
	# words_filtered = [ w for w in words if not w in stopwords]
	words_filtered = []
	for w in words:
		if w not in stop_words:
			words_filtered.append(w)
	
	frequencies = Counter(words_filtered)
	
	for term, tf in frequencies.items():
		print("%s\t%s" % (page["docID"], json.dumps((term, tf))))
