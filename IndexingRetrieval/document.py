from tornado.ioloop import IOLoop
from tornado import web, gen, httpserver, httpclient
from tornado import process, netutil
import pickle
import json
import hashlib
import getpass
from IndexingRetrieval import inventory


SNIPPET_LEN = 300
WIKI_URL = 'https://en.wikipedia.org/wiki/'


class DocumentHandler(web.RequestHandler):
    def initialize(self, docStore):
        self.docStore = docStore

    @gen.coroutine
    def get(self):
        docID = self.get_argument('id')
        q = self.get_argument('q')
        queryList = q.replace('%20', ' ').split()

        docDict = self.docStore
        
        # get title, url, snippet of document
        results = []
        results.append({})
        
        if docID in docDict.keys():
            results[0]['title'] = docDict[docID][0]
            results[0]['url'] = WIKI_URL + results[0]['title'].replace(' ', '_')
            text = docDict[docID][1]
            snippet = ''

            # get a relevant chunk of text to generate snippet
            for q in queryList:
                query = q.lower()
                queryPos = int(text.lower().find(query))
                if queryPos > 0:
                    if queryPos < SNIPPET_LEN:
                        snippet += text[0 : queryPos]
                    else:
                        snippet += '...' + text[queryPos-SNIPPET_LEN : queryPos]
                    snippet += "<strong>" + query + "</strong>"
                    if queryPos + len(query) + SNIPPET_LEN > len(text):
                        snippet += text[queryPos+len(query):]
                    else:
                        snippet += text[queryPos+len(query) : queryPos+len(query)+SNIPPET_LEN] + '...'
                    break;

            if len(snippet) == 0:
                snippet += text[0:SNIPPET_LEN]

            results[0]['snippet'] =snippet

        # {"results": [{"title": "Result 1", "url": "http://...", "snippet": "Ipsum lorem bacon ..."}]}
        self.write(json.dumps({"results": results}))
        self.finish()