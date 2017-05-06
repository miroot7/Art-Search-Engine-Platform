#!/usr/bin/env python3
#input (doc_id, (title, body))
#it sets the document store's entry for doc_id to (title, body). 

import sys, json, pickle

docStore = dict()
#data = map(lambda x: x.strip().split('\t'), sys.stdin)
for line in sys.stdin:
	value = line.strip().split('\t')
	docBody = json.loads(value[1])
	docStore[value[0]] = docBody

print(pickle.dump(docStore, sys.stdout.buffer))
