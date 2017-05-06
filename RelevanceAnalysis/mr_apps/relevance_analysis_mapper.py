#!/usr/bin/env python3

import sys
import re
import json
import nltk
from collections import Counter
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import string
from nltk.stem.snowball import SnowballStemmer
import re


NUM_RELEVANT_WORDS = 5

for line in sys.stdin:
    article = json.loads(line)
    text = str(article['docText'].lower())
    text = "".join(l for l in text if l not in string.punctuation)
    text = re.sub(r'\{\{.*?\}\}', '', text, flags=re.S)
    text = re.sub(r'<ref>.*?</ref>', '', text, flags=re.S)
    text = re.sub(r'\[\[File:.*?\|.*?\|.*?\|(.*?)\]\]', r'\1', text, flags=re.S)
    UGLY_TEXT_MAP = dict([(ord(char), None) for char in '[]{}'] + [(ord(char), ' ') for char in '|=*\\#'])
    text = text.translate(UGLY_TEXT_MAP)
    text = text.replace("'''", '"').replace("''", '"')
    text = text.strip()
    textwords = nltk.word_tokenize(text)

    stop_words = set(stopwords.words('english'))
    stop_words_file = open('DistributedIndexer/criteria/stopwordsList')
    stop_words_list = stop_words_file.read().splitlines()
    for w in stop_words_list:
        stop_words.add(w)

    #remove verbs
    textwords = nltk.pos_tag(textwords)
    words=[]
    for i in textwords:
        if i[1].startswith('V'):
            continue
        else:
            words.append(i[0])
    

    words_filtered = []
    for w in words:
        if w not in stop_words:
            words_filtered.append(w)
    

    term_freq = Counter(words_filtered)
    res = sorted(term_freq.items(), key=lambda d: d[1], reverse=True)
    
    if len(res)<NUM_RELEVANT_WORDS:
        for idx in range(len(res)):
            term = res[idx][0]
            tf = res[idx][1]
            print('%s\t%s' % (article['docID'], json.dumps((term, tf))))
    else:
        for idx in range(NUM_RELEVANT_WORDS):
            term = res[idx][0]
            tf = res[idx][1]
            print('%s\t%s' % (article['docID'], json.dumps((term, tf))))