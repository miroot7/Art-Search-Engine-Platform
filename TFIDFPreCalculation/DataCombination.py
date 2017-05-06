import os
import json
from collections import defaultdict


def combineInvIndex():

	combined = dict()

	input_path = 'DataFiltering/targets/'
	infs = [f for f in os.listdir(input_path) if f.endswith('.in')]
	infiles = [os.path.join(input_path, f) for f in infs]


	outs = open('TFIDFPreCalculation/tfidf_data/data', 'w')
	for f in infiles:
		tmp = open(f,"r")
		for line in tmp:
			page = json.loads(line)
			outs.write(json.dumps(page) + "\n")


if __name__ == '__main__':
	combineInvIndex()