from assignment2 import Inventory
from assignment2 import FrontEndHandler
import tornado.ioloop
import tornado.web
from tornado import gen ,web
from tornado.httpclient import AsyncHTTPClient
import math
import numpy as np
import json
import pickle
import hashlib
import logging

SETTINGS = {'static_path': Inventory.WEBAPP_PATH}
log = logging.getLogger(__name__)

#receives queries via its GET method in response it uses its inverted index to return a JSON-encoded ranked list of (docID, score) pairs that best match the query.
#partitioned index servers that use the inverted index to retrieve document IDs containing a given query term
#{"postings": [[231, 28.60], [186, 9.53]]}
class IndexServerHandler(tornado.web.RequestHandler):

	@gen.coroutine
	def get(self):
		hostAddr = self.request.host
		portN = int(str(hostAddr)[(str(hostAddr).index(':') + 1):])%Inventory.NUM_INDEX_PART
		postings = {}
		query = self.get_argument('q').replace('%20', ' ').split()
		#it first uses the document frequency table to create a vector-space representation of the query.
		invertedIndexTable = pickle.load(open('DistributedIndexer/invindex_jobs/' + str(portN) + '.out', 'rb'))
		IDFmap = pickle.load(open('DistributedIndexer/idf_jobs/0.out', 'rb'))
		#Each dimension of the vector should be set to the corresponding term's TF-IDF value.
		queryV = []
		docVectors = {}
		idx = 0
		for word in query:
			if word not in IDFmap:
				queryV.append(0)
			else:
				#For the query, you can set the TF of each term to 1
				queryV.append(IDFmap[word])
				if word in invertedIndexTable:
					for i in range(0, len(invertedIndexTable[word])):
						if invertedIndexTable[word][i][0] not in docVectors:
							docVectors[invertedIndexTable[word][i][0]]=[]
							for index in range(0, idx):
								docVectors[invertedIndexTable[word][i][0]].append(0)
							docVectors[invertedIndexTable[word][i][0]].append(invertedIndexTable[word][i][1]*queryV[idx])	
						else:
							docVectors[invertedIndexTable[word][i][0]].append(invertedIndexTable[word][i][1]*queryV[idx])
				for vector in docVectors.values():
					if len(vector) < idx+1 :
						vector.append(0)
			idx += 1
		#The documents are then scored. 
		#Each document's score is the inner product (a.k.a. dot product, effectively correlation here) of its vector and the query vector. 
		#In addition, scores should be biased so that documents with the query terms in their title receive especially high scores.
		docs = np.array(list(docVectors.values()))
		queryVector = np.array(queryV)
		innerProducts = np.inner(docs,queryVector)
		index = 0
		scores = {}
		for doc in docVectors.keys():
			scores[doc] = innerProducts[index]
			index += 1
		sortedScores = sorted(scores.items(), key  = lambda x : -x[1])
		#Finally, the K highest-scoring documents are written out as a JSON-encoded list of (docID, score) pairs.
		topK = min(10, len(sortedScores))
		postings['postings'] = []
		for i in range(0, topK):
			postings['postings'].append(list(sortedScores[i]))
		self.write(json.dumps(postings))
		self.finish()



class DocumentServerHandler(tornado.web.RequestHandler):
	@gen.coroutine
	def get(self):
	#A document server is also an HTTP server. 
	#It receives requests via its GET method that consist of a document ID and a query. 
	#In response, it uses its document store to return detailed document data (title, URL, and snippet).
	#The snippet should be a relevant chunk of text from the document, and terms from the query should be emphasized. 	
	#The output should be JSON-encoded.
		docID = self.get_arguments('id')
		portN = int(hashlib.md5(str(docID[0]).encode()).hexdigest()[:8], 16) % int(Inventory.NUM_DOCUMENT_PART)
		docStore = pickle.load(open('DistributedIndexer/docs_jobs/' + str(portN) + '.out', 'rb'))
		results = {}
		query = self.get_argument('q').replace('%20', ' ').split()
		docs = []
		for Id in docID:
			if Id in docStore: 
				text = docStore[Id][1]
				flag = True
				for word in query:
					if text.find(word) > 0 : 
						flag = False
						if(text.find(word)>30):
							if (text.find(word) + 50 < len(text)):
								snippet = '...' + text[text.index(word)-30:text.index(word)+50] + '...'
							else:
								snippet = '...' + text[text.index(word)-30:]
						else:
							if (text.find(word) + 50 < len(text)):
								snippet = text[0:text.index(word)+50] + '...'
							else: 
								snippet = text
						break
				if flag: 
					if(len(text)>80):
						snippet = text[0:80]
					else:
						snippet = text
				for word in query:
					snippet = snippet.replace(word, '<strong>' + word + '</strong>')
				url = 'https://en.wikipedia.org/wiki/' + docStore[Id][0].replace(' ', '_')
				docs.append({'title' : docStore[Id][0], 'url' : url, 'snippet' : snippet})
		results['results'] = docs
		self.write(json.dumps(results)) 
		self.finish()


class IndexDotHTMLAwareStaticFileHandler(tornado.web.StaticFileHandler):
    def parse_url_path(self, url_path):
        if not url_path or url_path.endswith('/'):
            url_path += 'index.html'
        return super(IndexDotHTMLAwareStaticFileHandler, self).parse_url_path(url_path)
        
if __name__ == '__main__':
	logging.basicConfig(format='%(levelname)s - %(asctime)s - %(message)s', level=logging.DEBUG)
	applicationFront = tornado.web.Application([(r'/search',  FrontEndHandler.FrontEndHandler), (r'/(.*)', IndexDotHTMLAwareStaticFileHandler, dict(path = SETTINGS['static_path']))], **SETTINGS)
    
	#applicationFront = tornado.web.Application([
                #(r'/search', FrontEndHandler.FrontEndHandler)])
	applicationIndexServers = []
	applicationDocumentServers= []
	for i in range(0, Inventory.NUM_INDEX_PART):
		applicationIndexServers.append(tornado.web.Application([
			(r'/index', IndexServerHandler),
		]))
		applicationIndexServers[i].listen(Inventory.BASE_PORT  + 1+i)
		log.info('Index server is listening on %d' % (Inventory.BASE_PORT  + i))
	for i in range(0, Inventory.NUM_DOCUMENT_PART):
		applicationDocumentServers.append(tornado.web.Application([
			(r'/doc', DocumentServerHandler),
		]))
		applicationDocumentServers[i].listen(Inventory.BASE_PORT + 1+ Inventory.NUM_INDEX_PART + i)
		log.info('Doc server is listening on %d' % (Inventory.BASE_PORT +  Inventory.NUM_INDEX_PART + i))
	applicationFront.listen(Inventory.BASE_PORT)
	log.info('Front end is listening on %d', Inventory.BASE_PORT)
	tornado.ioloop.IOLoop.current().start()



