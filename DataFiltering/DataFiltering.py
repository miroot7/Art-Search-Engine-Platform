import argparse
import xml.etree.cElementTree as ET
import json
import csv
import os


def main():
	titles = set ()
	with open('criteria/Artworks.csv') as csvFile: 
		spamreader = csv.reader(csvFile)
		for row in spamreader: 
			#print(row[0])
			rowList = row[0].split(',')
			titles.add(rowList[0])
	with open('criteria/Artists.csv') as csvFile1: 
		spamreader = csv.reader(csvFile1)
		for row in spamreader: 
			titles.add(row[1])

	# python3 -m reformatter data/enwiki-latest-pages-articles-multistream.xml --job_path=targets/ --num_partitions=10
	parser = argparse.ArgumentParser()
	parser.add_argument("input")
	parser.add_argument("--job_path")
	parser.add_argument("--num_partitions")
	args = parser.parse_args()


	inFile = args.input
	job_path = args.job_path
	num_partitions = int(args.num_partitions)
	#partitions = [ET.Element('Root') for i in range(num_partitions)]
	inputs = [open("{0}/{1}.in".format(job_path, i), "w") for i in range(num_partitions)]

	context = ET.iterparse(inFile, events=('end', ))
	#print("Parse completed.")
	prefix = "{http://www.mediawiki.org/xml/export-0.10/}"
	count = 1
	for event, elem in context:
		if elem.tag == (prefix + "page"):
			title = elem.find(prefix + "title").text
			if title in titles:
				print("%d\t%s" % (count, title))
				count = count + 1
				docID = elem.find(prefix + "id").text
				docText = elem.find(prefix + "revision").find(prefix + "text").text
				index = int(docID) % num_partitions
				#partitions[index].append(elem)
				inputs[index].write(json.dumps({"title": title, "docID": docID, "docText": docText}) + "\n")
			elem.clear()

	print(count)

"""
	for n in range(num_partitions):		
		ET.register_namespace("", "http://www.mediawiki.org/xml/export-0.10/")
		#inputs[index].write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n")
		inputs[n].write(ET.tostring(partitions[n]))
"""

if __name__ == '__main__':
	main()