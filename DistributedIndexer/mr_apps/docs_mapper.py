#!/usr/bin/env python3


#The mapper's job is to associate each document with that document's title and body. 
#The mapper takes as input a data file partition written by the reformatter. 
#outputs key-value pairs of the form (doc_id, (title, body)). 

import json
import sys
import mwparserfromhell
import re

for line in sys.stdin:
	page = json.loads(line)
	text = page['docText']
	parsed_wikicode = mwparserfromhell.parse(text,skip_style_tags=True).strip_code(normalize=True, collapse=True)
	text = str(parsed_wikicode)
	text = re.sub(r'\{\{.*?\}\}', '', text, flags=re.S)
	text = re.sub(r'<ref>.*?</ref>', '', text, flags=re.S)
	text = re.sub(r'\[\[File:.*?\|.*?\|.*?\|(.*?)\]\]', r'\1', text, flags=re.S)
	UGLY_TEXT_MAP = dict([(ord(char), None) for char in '[]{}'] + [(ord(char), ' ') for char in '|=*\\#'])
	text = text.translate(UGLY_TEXT_MAP)
	text = text.replace("'''", '"').replace("''", '"')
	text = text.strip()




	print("%s\t%s" % (page["docID"], json.dumps((page["title"], text))))
