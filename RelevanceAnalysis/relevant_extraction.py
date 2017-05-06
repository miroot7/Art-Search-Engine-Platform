#!/use/bin/env python3

from tornado.ioloop import IOLoop
from tornado import web, gen, process, httpserver, httpclient
import socket
import os.path
import json
import pickle
from collections import defaultdict
from IndexingRetrieval import inventory, index, document
import logging

log = logging.getLogger(__name__)


NUM_RELEVANT_WORDS = 5
MAX_RESULT_PER_WORD = 2

class RelevanceExtractingHandler(web.RequestHandler):
    
    @gen.coroutine
    def get(self):
        # http://localhost:port/search?idx_job=0
        idx_job = self.get_argument('idx_job')
        docID_words = pickle.load(open('RelevanceAnalysis/relevance_jobs/%s.out' % idx_job, 'rb'))

        # format of term_relevance_docs cache: ['term'] = ['docID1', 'docID2']
        """
        cache_dict = defaultdict(list)
        if os.path.exists('RelevanceAnalysis/cache_jobs/cache'):
            cache = open('RelevanceAnalysis/cache_jobs/cache',"r")
            for line in cache:
                key = json.loads(line)[0]
                value = json.loads(line)[1]
                cache_dict[key] = value
        """


        docID_releventDocs = defaultdict(list)
        count = 0

        for docID in docID_words:
            releventDocs = []
            storedDocs = []
            storedDocs.append(docID)
            for i in range(len(docID_words[docID])):
                query = docID_words[docID][i][0]
                print(query)
                """
                if query in cache_dict.keys():
                    docIDs = cache_dict[query]
                    for i in range(len(docIDs)):
                        releventDocs.append((docIDs[i], query))
                else:
                """

                httpclient.AsyncHTTPClient.configure(None, defaults={'connect_timeout':300, 'request_timeout':300})
                http_client_index = httpclient.AsyncHTTPClient()
                indexServerRequest = yield [http_client_index.fetch(server + query) for server in inventory.indexServers]


                docIDs = []
                for request in indexServerRequest:
                    docIDs += json.loads(request.body.decode())["postings"]
                
                docIDs.sort(key=lambda x: -x[1])

                num_result = min(MAX_RESULT_PER_WORD, len(docIDs))
                docIDs_query = []

                releventDocs_per_query = []
                for d in docIDs:
                    if d[0] in storedDocs:
                        continue
                    else:
                        releventDocs_per_query.append((d[0], query))
                        storedDocs.append(d[0])
                        # cache_dict[query].append(d[0])
                    if len(releventDocs_per_query) == num_result:
                        break

                releventDocs += releventDocs_per_query

                #append_cache = open('RelevanceAnalysis/cache_jobs/cache',"a")
                #append_cache.write(json.dumps((query, cache_dict[query])) + "\n")


            count += 1
            print("%s has extracted %d docs" % (idx_job, count))
            
            for i in range(len(releventDocs)):
                print(releventDocs[i])


            docID_releventDocs[docID] = releventDocs


        pickle.dump(docID_releventDocs, open('IndexingRetrieval/relevance_docs/tmpDocs/relevantDocs' + str(idx_job), 'wb'))
        self.finish()


def startServers(): 
    inverted_index = pickle.load(open(inventory.InvIndex_Path, 'rb'))
    idf = pickle.load(open(inventory.IDF_Path,'rb'))
    tf_idf = pickle.load(open(inventory.TFIDF_Path, 'rb'))
    words = pickle.load(open(inventory.Words_Path,'rb'))


    app = web.Application([(r"/search", RelevanceExtractingHandler)])
    app.listen(inventory.BASE_PORT)
    log.info('Front end is listening on %d', inventory.BASE_PORT)


    for i in range(inventory.NUM_INDEX_PART):
        indexPort = inventory.BASE_PORT + 1 + i
        applicationIndexServer = web.Application([(r'/index', index.IndexHandler, dict(MAX_RESULT = 10, inverted_index=inverted_index, idf=idf, tf_idf=tf_idf, words=words))])
        applicationIndexServer.listen(indexPort)
        log.info('Index server is listening on %d' % (indexPort))


    IOLoop.instance().start()

if __name__ == "__main__":
    logging.basicConfig(format='%(levelname)s - %(asctime)s - %(message)s', level=logging.DEBUG)
    startServers()

