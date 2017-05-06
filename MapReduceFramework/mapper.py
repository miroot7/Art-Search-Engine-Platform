#!/use/bin/env python3

from tornado.ioloop import IOLoop
from tornado import web, gen, httpclient
import json
import urllib
import subprocess
import hashlib, getpass
import uuid
from collections import defaultdict
from itertools import chain
import re
import pickle



class MapHandler(web.RequestHandler):
    
    mapOutput = dict()

    @gen.coroutine
    def get(self):
        ## /map?mapper_path=wordcount/mapper.py&input_file=fish_jobs/0.in&num_reducers=1
        mapper_path = self.get_argument('mapper_path')
        input_file = self.get_argument('input_file')
        num_reducers = self.get_argument('num_reducers')
        mapper_path = mapper_path.replace('%2F','/')
        input_file = input_file.replace('%2F', '/')
        num_reducers = int(num_reducers)


        if (re.match("RelevanceAnalysis*", input_file)):
            inf = pickle.load(open(input_file,'rb'))
        else:
            inf = open(input_file)

        p = subprocess.Popen(mapper_path, stdin=inf, stdout=subprocess.PIPE)
        (out, _) = p.communicate()
        inf.close()

        kv_pairs = []
        outputs = out.decode().split('\n')
        kv_pairs = [line.split('\t') for line in outputs if len(line)>0]
        kv_pairs.sort(key = lambda x : x[0])


        ## [[["key", "value"], ["key", "value"], ...],["key", "value"], ["key", "value"], ...], ...]
        kv_list = [[] * 1 for i in range(int(num_reducers))]
        for k, v in kv_pairs:
            lists_idx = int(hashlib.md5(k.encode()).hexdigest()[:8],16) % int(num_reducers)
            kv_list[lists_idx].append([k,v])


        ## {"map_task_id1": [[[k,v],[k,v], ...],[[k,v],[k,v], ...],...], "map_task_id2": ...}
        map_task_id = str(uuid.uuid4())
        self.mapOutput[map_task_id] = kv_list

        ## {"map_task_id": "7b89bcf7716230c9fafd7b21e32f24c7", "status": "success"}
        self.write(json.dumps({"map_task_id": map_task_id, "status": "success"}))
        self.finish()



class RetrieveMapOutputHandler(web.RequestHandler):
    @gen.coroutine
    def get(self):
        ## /retrieve_map_output?reducer_ix=0&map_task_id=6a75d424315ba28ecdd901976b7833e8
        reducer_ix = self.get_argument('reducer_ix')
        map_task_id = self.get_argument('map_task_id')

        ## [["key", "value"], ["key", "value"], ...]
        map_output = MapHandler.mapOutput[map_task_id][int(reducer_ix)]

        self.write(json.dumps(map_output))
        self.finish()