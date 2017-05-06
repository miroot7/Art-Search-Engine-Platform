import tornado.web
from tornado import gen
from tornado.httpclient import AsyncHTTPClient
import json
import pickle
import hashlib
from . import inventory

class FrontHandler_777(tornado.web.RequestHandler):
    def initialize(self, doc_1_10_dict, retrieved_cache):
        self.doc_1_10_dict = doc_1_10_dict
        self.retrieved_cache = retrieved_cache

    
    @gen.coroutine
    def get(self):
        query = self.get_argument('q').replace(' ', '%20')
        doc_1_10_dict = self.doc_1_10_dict
        retrieved_cache = self.retrieved_cache


        http_client = AsyncHTTPClient()

        related_doc_list = []
        if query in retrieved_cache.keys():
            related_doc_list = retrieved_cache[query]
        else:
            listOfDocID = []
            for i in range(len(inventory.indexServers)):
                response = yield http_client.fetch(inventory.indexServers[i] + query)
                postings = json.loads(response.body.decode('utf-8'))
                for l in postings['postings']:
                    listOfDocID.append(l)

            if len(listOfDocID) != 0:
                # The doc_id of the doc that has highest score.
                doc_id_for_reference = listOfDocID[0][0]
                # Retrieve 10 doc_ids.
                related_doc_list.append((str(doc_id_for_reference), query))
                related_doc_list += doc_1_10_dict[doc_id_for_reference]
                retrieved_cache[query] = related_doc_list 


        # Fetch url, title, snippet from document servers
        results = []
        dic_to_add = {}
        if len(related_doc_list) == 0:
            self.write(json.dumps('Can not find any result, plz wait for our future work heheda:)'))
            dic_to_add[query] = []
            pickle.dump(dic_to_add, open('to_add_query', 'ab'))
        else:
            futures = []
            for doc in related_doc_list:
                docID = doc[0]
                term = doc[1]
                idx = int(hashlib.md5(docID.encode()).hexdigest()[:8],16) % int(inventory.NUM_DOCUMENT_PART)
                url = inventory.documentServers[idx] + str(docID) + "&q=" + term
                futures.append(http_client.fetch(url))
            documentServerRequest = yield futures

            results = []
            for request in documentServerRequest:
                results += json.loads(request.body.decode())["results"]

            # Post results
            self.write(json.dumps({"results": results}))
            append_cache = open(inventory.RetrievedCache_Path,'a')
            append_cache.write(json.dumps((query, retrieved_cache[query])) + "\n")

        self.finish()

