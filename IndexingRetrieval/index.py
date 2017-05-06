#!/use/bin/env python3

from tornado.ioloop import IOLoop
from tornado import web, gen, httpserver, httpclient, process, netutil
from tornado import process, netutil
from IndexingRetrieval import inventory
import pickle
import json
import os
import numpy as np
import math
import urllib
from sklearn import feature_extraction
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.feature_extraction.text import CountVectorizer
import sys
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from collections import Counter
import string
import logging
import scipy.sparse
from scipy.sparse import csr_matrix
from nltk.stem.snowball import SnowballStemmer
import time


class IndexHandler(web.RequestHandler):
    def initialize(self, MAX_RESULT, inverted_index, idf, tf_idf, words):
        self.MAX_RESULT = MAX_RESULT
        self.inverted_index = inverted_index
        self.idf = idf
        self.tf_idf = tf_idf
        self.words = words


    @gen.coroutine
    def get(self):
        postings = {}
        stemmer = SnowballStemmer("english")
        query = self.get_argument('q').replace('%20', ' ').split()
        query = [word.strip('{}()#|') for word in query]
        query = [stemmer.stem(word) for word in query]


        timeStart = time.time()

        MAX_RESULT = self.MAX_RESULT
        inverted_index = self.inverted_index
        idf = self.idf
        tf_idf = self.tf_idf
        words = self.words

        # print(time.time()-timeStart)

        #idff = pickle.load(open('TFIDFPreCalculation/tfidf_data/idf','rb'))
    
        query_indices=[]
        remove_list =[]
        for i in range(len(query)):
            if query[i] in words:
                query_indices.append(words.index(query[i]))
            else:
                remove_list.append(query[i])
        for i in remove_list:
            query.remove(i)
        #query = list(set(query)-set(remove_list))
        if len(query)>0:
            feature_indice=set()
            for i in query_indices:         
                feature_index = inverted_index[:,i].nonzero()[0]
                feature_indice.add(x for x in feature_index)

            #feature_index = inverted_index[:,i].nonzero()[0]
            
            query_idf =[]
            for i in range(len(query)):
                query_idf.append(idf[query_indices[i]])
            #query_idf = idf[query[0]]
            feature_indices=[]
            for i in feature_index:
                feature_indices.append(i)
           

            tfidf_scores=[]
            for x in range(len(feature_indices)):
                tf=[]
                for j in range(len(query_indices)):
                    tf.append(tf_idf[feature_indices[x],query_indices[j]])

            #index+=1
                tfidf_scores.append(tf)


            #timeStart= time.time()
            #print('get scores')

            s = np.inner(query_idf,tfidf_scores)
            #print(time.time()-timeStart)


            index = 0
            scores = {}
            for doc in feature_indices:
                scores[str(doc)] = s[index]
                index += 1

            sortedScores = sorted(scores.items(), key  = lambda x : -x[1])

            #print(type(sortedScores))

            topK = min(MAX_RESULT, len(sortedScores))


            postings['postings'] = []
            for i in range(topK):
                key = sortedScores[i][0]
                value = sortedScores[i][1]
                postings['postings'].append([key,value])
        else:
            postings['postings'] = []
        
        self.write(json.dumps(postings))
        self.finish()
