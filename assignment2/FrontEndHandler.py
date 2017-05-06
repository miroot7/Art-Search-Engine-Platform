import tornado.ioloop
import tornado.web
from tornado import gen
from tornado.httpclient import AsyncHTTPClient
import json
from assignment2 import Inventory

#receive queries at the URL /search?q=query_here
#sends it to each of the N index servers
#receives back N lists of (document ID, score)
#merge lists
#top k kept
#find document server using docId mod number of partition
#document server queried for the title, URL, and snippet corresponding to document id and query
#write results out in JSON format. return maximum of ten.

#a frontend server that coordinates the activities of the index and document servers
class FrontEndHandler(tornado.web.RequestHandler):
	@gen.coroutine
	def get(self):
		#receive queries at the URL /search?q=query_here
		query = self.get_argument('q').replace(' ', '%20')
		#sends it to each of the N index servers
		#print(self.port)
		mergeList = []
		documents = []
		http_client = AsyncHTTPClient()
		for i in range(0,Inventory.NUM_INDEX_PART):
			http = Inventory.indexServers[i] + query
			response = yield http_client.fetch(http) #returns HTTPResponse 
			decodeResponse = response.body.decode()
			evaluation = json.loads(decodeResponse)
			#merge lists
			mergeList.extend(evaluation['postings'])
			#sort mergelist by score and keep top 10
		mergeList.sort(key = lambda x : -x[1])
		topDocs = []
		topK = min(10, len(mergeList))
		for i in range(0, topK):
			topDocs.append(mergeList[i])
		for i in range(0, topK):
			#find document server using docId mod number of partition
			docServerIndex = int(topDocs[i][0]) % Inventory.NUM_DOCUMENT_PART
			docServer = Inventory.documentServers[docServerIndex]+str(topDocs[i][0])+"&q="+query
			#document server queried for the title, URL, and snippet corresponding to document id and query
			response = yield http_client.fetch(docServer)
			decodeResponse = response.body.decode()
			evaluation = json.loads(decodeResponse)
			documents.append(evaluation['results'][0])
		results = {}
		results['num_results'] = len(documents)
		results['results'] = documents
		self.write(json.dumps(results))
		self.finish()

if __name__ == '__main__':
    Example().run()

    

