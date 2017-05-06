#!/usr/bin/env python3

import sys
import pickle
import json


invertedIndex = {}

for line in sys.stdin:
	pair = line.strip().split("\t")
	if json.loads(pair[1])[0] in invertedIndex:
		invertedIndex[json.loads(pair[1])[0]].append((pair[0], json.loads(pair[1])[1]))
	else:
		invertedIndex[json.loads(pair[1])[0]] = [(pair[0], json.loads(pair[1])[1])]

sys.stdout.buffer.write(pickle.dumps(invertedIndex))