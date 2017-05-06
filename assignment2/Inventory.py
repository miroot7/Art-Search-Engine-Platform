import hashlib, getpass
import socket


NUM_INDEX_PART = 4
NUM_DOCUMENT_PART = 4


MAX_PORT = 49152
MIN_PORT = 10000
BASE_PORT = int(hashlib.md5(getpass.getuser().encode()).hexdigest()[:8], 16) % \
    (MAX_PORT - MIN_PORT) + MIN_PORT


BASE_PORT += 30

host = "http://127.0.0.1:"

frontendServer = host + str(BASE_PORT) + "/search"

indexServers = []
for n in range(1,  NUM_INDEX_PART+1):
    indexServers.append(host + str(BASE_PORT + n) + "/index?q=")

documentServers = []
for m in range(1,  NUM_DOCUMENT_PART+1):
    documentServers.append(host + str(BASE_PORT + NUM_INDEX_PART + m) + "/doc?id=")


InvIndex_Path = 'TFIDFPreCalculation/tfidf_data/inverted-index'
TFIDF_Path = 'TFIDFPreCalculation/tfidf_data/tf-idf-matrix'
Words_Path = 'TFIDFPreCalculation/tfidf_data/words'
IDF_Path = 'DistributedIndexer/idf_jobs/0.out'
Docs_Path = 'DistributedIndexer/docs_jobs/%d.out'
Doc_1_10_dict_Path = 'IndexingRetrieval/relevance_docs/relevantDocs'
RetrievedCache_Path = 'IndexingRetrieval/retrieved_cache/retrievedCache'
WEBAPP_PATH = "webapp/"
