from tornado.ioloop import IOLoop
from tornado import web, gen, httpserver, httpclient
from tornado import process
import socket
import json
from IndexingRetrieval import inventory, frontend_777, index, document
import math
import numpy as np
import json
import pickle
import tornado, pickle, logging, urllib
from tornado.ioloop import IOLoop
from tornado import web, gen, process, httpserver, httpclient, netutil
from itertools import chain
from collections import defaultdict


SETTINGS = {'static_path': inventory.WEBAPP_PATH}

log = logging.getLogger(__name__)


class IndexDotHTMLAwareStaticFileHandler(web.StaticFileHandler):
    def parse_url_path(self, url_path):
        if not url_path or url_path.endswith('/'):
            url_path += 'index.html'
        return super(IndexDotHTMLAwareStaticFileHandler, self).parse_url_path(url_path)

# inverted_index, idf, tf_idf, doc_ids, words, doc_1_10_dict, docStore
def startServers():
    doc_1_10_dict = pickle.load(open(inventory.Doc_1_10_dict_Path, 'rb'))
    inverted_index = pickle.load(open(inventory.InvIndex_Path, 'rb'))
    idf = pickle.load(open(inventory.IDF_Path,'rb'))
    tf_idf = pickle.load(open(inventory.TFIDF_Path, 'rb'))
    words = pickle.load(open(inventory.Words_Path,'rb'))


    retrieved_cache = defaultdict(list)
    tmp  = open(inventory.RetrievedCache_Path,'r')
    for line in tmp:
        key = json.loads(line)[0]
        value = json.loads(line)[1]
        retrieved_cache[key] = value


    applicationFront = tornado.web.Application([(r'/search',  frontend_777.FrontHandler_777, dict(doc_1_10_dict = doc_1_10_dict, retrieved_cache = retrieved_cache)),(r'/(.*)', IndexDotHTMLAwareStaticFileHandler, dict(path = SETTINGS['static_path']))], **SETTINGS)
    applicationFront.listen(inventory.BASE_PORT)
    log.info('Front end is listening on %d', inventory.BASE_PORT)


    for i in range(inventory.NUM_INDEX_PART):
        indexPort = inventory.BASE_PORT + 1 + i
        applicationIndexServer = tornado.web.Application([(r'/index', index.IndexHandler, dict(MAX_RESULT = 1, inverted_index=inverted_index, idf=idf, tf_idf=tf_idf, words=words))])
        applicationIndexServer.listen(indexPort)
        log.info('Index server is listening on %d' % (indexPort))


    for i in range(inventory.NUM_DOCUMENT_PART):
        docPort = inventory.BASE_PORT + inventory.NUM_INDEX_PART + 1 + i
        docStore = pickle.load(open(inventory.Docs_Path % (i), 'rb'))
        applicationDocumentServer = tornado.web.Application([(r'/doc', document.DocumentHandler, dict(docStore=docStore))])
        applicationDocumentServer.listen(docPort)
        log.info('Doc server is listening on %d' % (docPort))
        
    IOLoop.instance().start()


if __name__ == '__main__':
    logging.basicConfig(format='%(levelname)s - %(asctime)s - %(message)s', level=logging.DEBUG)
    startServers()
