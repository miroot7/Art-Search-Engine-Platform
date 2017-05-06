#!/usr/bin/env python3

import sys
import json
import pickle

res = dict()

for line in sys.stdin:
    docID, term_tf = line.strip().split('\t')
    term_tf = (json.loads(term_tf)[0], json.loads(term_tf)[1])
    
    if docID not in res:
        res[docID] = [term_tf]
    else:
        res[docID].append(term_tf)

sys.stdout.buffer.write(pickle.dumps(res))