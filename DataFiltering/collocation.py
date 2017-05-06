import sys
import nltk
import json
import os
#nltk.download('punkt')
#nltk.download('corpora')
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from collections import Counter
import string
from math import log
import re
import pickle
from nltk.probability import FreqDist, LidstoneProbDist
from nltk.probability import ConditionalFreqDist as CFD
from nltk.util import tokenwrap, LazyConcatenation
from nltk.metrics import f_measure, BigramAssocMeasures
from nltk.collocations import BigramCollocationFinder

input_path = 'DataFiltering/targets/'
infs = [f for f in os.listdir(input_path) if f.endswith('.in')]
infiles = [os.path.join(input_path, f) for f in infs]
out = open('DataFiltering/collocations.out','w')

for f in infiles:
        tmp = open(f,'r')
        for line in tmp:
                page = json.loads(line)
                text = str(page["docText"]).lower()
                text = "".join(l for l in text if l not in string.punctuation)
                text = re.sub(r'\{\{.*?\}\}', '', text, flags=re.S)
                text = re.sub(r'<ref>.*?</ref>', '', text, flags=re.S)
                text = re.sub(r'\[\[File:.*?\|.*?\|.*?\|(.*?)\]\]', r'\1', text, flags=re.S)
                UGLY_TEXT_MAP = dict([(ord(char), None) for char in '[]{}'] + [(ord(char), ' ') for char in '|=*\\#'])
                text = text.translate(UGLY_TEXT_MAP)
                text = text.replace("'''", '"').replace("''", '"')
                text = text.strip()


                textwords = nltk.word_tokenize(text)
                finder = BigramCollocationFinder.from_words(textwords)
                stop_words = set(stopwords.words('english'))
                finder.apply_freq_filter(3)
                finder.apply_word_filter(lambda w: len(w) < 3 or w.lower() in stop_words)
                bigram_measures = BigramAssocMeasures()
                collocations = finder.nbest(bigram_measures.likelihood_ratio, 5)
                for w1,w2 in collocations:
                        out.write(w1+' '+w2+'\n')



