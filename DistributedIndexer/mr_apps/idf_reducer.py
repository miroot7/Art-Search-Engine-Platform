#!/usr/bin/env python3

 
#input the (term, doc_id) pairs from the mapper. For each such input pair, it adds 1 to the document count for term. 
#, the total number of documents in the corpus is tracked by adding each document ID to a set called doc_ids. 
#The inverse document frequency for each term is computed as log(len(doc_ids) / document_count[term]). 
#Finally, this IDF map is pickled and written directly to stdout. 

from itertools import groupby
from operator import itemgetter
import sys
import math
import pickle

docIDs = set()
IDFmap = dict()

data = map(lambda x: x.strip().split('\t'), sys.stdin)

for key, group in groupby(data, lambda x : x[0]):
	for key, docID in group:
		docIDs.add(docID)
		if key in IDFmap:
			IDFmap[key] = IDFmap[key] + 1
		else:
			IDFmap[key] = 1

for key in IDFmap:
	IDFmap[key] = math.log10(len(docIDs) / IDFmap[key])

print(pickle.dump(IDFmap, sys.stdout.buffer))
