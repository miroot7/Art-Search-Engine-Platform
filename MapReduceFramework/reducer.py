#!/use/bin/env python3

from tornado.ioloop import IOLoop
from tornado import web, gen, httpclient
import json
import re
import pickle
import urllib, subprocess
from MapReduceFramework import inventory
import logging


class ReduceHandler(web.RequestHandler):
    @gen.coroutine
    def get(self):
        ## /reduce?reducer_ix=0&reducer_path=wordcount/reducer.py&map_task_ids=map_task_id1,map_task_id2&job_path=fish_jobs
        reducer_ix = self.get_argument('reducer_ix')
        reducer_path = self.get_argument('reducer_path')
        reducer_path = reducer_path.replace('%2F','/')
        map_task_ids_str = self.get_argument('map_task_ids')
        map_task_ids_str = map_task_ids_str.replace('%2C',',')
        map_task_ids = map_task_ids_str.split(',')
        job_path = self.get_argument('job_path')
        job_path = job_path.replace('%2F', '/')


        num_mappers = len(map_task_ids)

        http = httpclient.AsyncHTTPClient()
        futures = []
        for i in range(num_mappers):
            server = inventory.workerServers[i % len(inventory.workerServers)]
            params = urllib.parse.urlencode({'reducer_ix': reducer_ix,
                'map_task_id': map_task_ids[i]})
            url = "%s/retrieve_map_output?%s" % (server, params)
            print("Fetching", url)
            futures.append(http.fetch(url))
        responses = yield futures


        kv_pairs = []
        for r in responses:
            kv_pairs.extend(json.loads(r.body.decode()))
        kv_pairs.sort(key=lambda x: x[0])

        kv_string = "\n".join([pair[0] + "\t" + pair[1] for pair in kv_pairs])
        if (re.match("relevance_docs*", job_path)):
            output = open(job_path + '/relevance_docs', 'w')
        else:
            output = open(job_path + '/' + str(reducer_ix) + '.out', 'w')
        p = subprocess.Popen(reducer_path, stdin=subprocess.PIPE, stdout=output)
        (out, _) = p.communicate(kv_string.encode())
        output.close()
        
        self.write(json.JSONEncoder().encode({"status": "success"}))
        self.finish()