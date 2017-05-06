#!/use/bin/env python3

import argparse
import os
import json
import re
import urllib
from tornado.ioloop import IOLoop
from tornado import web, gen, httpclient
from MapReduceFramework import inventory


@gen.coroutine
def coordinator():
    parser = argparse.ArgumentParser(description='Process command-line arguments')
    parser.add_argument('--mapper_path', dest='mapper_path')
    parser.add_argument('--reducer_path', dest='reducer_path')
    parser.add_argument('--input_path', dest='input_path')
    parser.add_argument('--job_path', dest='job_path')
    parser.add_argument('--num_reducers', dest='num_reducers')
    args = parser.parse_args()


    if re.match("RelevanceAnalysis*", args.input_path):
        infs = [f for f in os.listdir(args.input_path) if f.endswith('.out')]
    else:
        infs = [f for f in os.listdir(args.input_path) if f.endswith('.in')]

    infiles = [os.path.join(args.input_path, f) for f in infs]
    num_mapper = len(infiles)


    httpclient.AsyncHTTPClient.configure(None, defaults={'connect_timeout':900000, 'request_timeout':900000})

    http = httpclient.AsyncHTTPClient()

    ## /map?mapper_path=wordcount/mapper.py&input_file=fish_jobs/0.in&num_reducers=1
    map_futures = []
    for i in range(num_mapper):
        server = inventory.workerServers[i % len(inventory.workerServers)]
        params = urllib.parse.urlencode({'mapper_path': args.mapper_path,
            'input_file': infiles[i],
            'num_reducers': args.num_reducers})
        ##url = "%s/map?%s" % (server, urllib.parse.unquote(params))
        url = "%s/map?%s" % (server, params)
        print("Mapper is working:", url)
        map_futures.append(http.fetch(url))
    map_responses = yield map_futures


    ## {"map_task_id": "e1baab8be3148c6eb23310d514220b32", "status": "success"}
    mapIds = []
    for r in map_responses:
        mapIds.append(json.loads(r.body.decode())['map_task_id'])
    map_task_ids = ",".join(ID for ID in mapIds)


    ## /reduce?reducer_ix=0&reducer_path=wordcount/reducer.py&map_task_ids=map_task_id1,map_task_id2&job_path=fish_jobs
    reduce_futures = []
    for i in range(int(args.num_reducers)):
        server = inventory.workerServers[i % len(inventory.workerServers)]
        params = urllib.parse.urlencode({'reducer_ix': i,
            'reducer_path': args.reducer_path,
            'map_task_ids': map_task_ids,
            'job_path': args.job_path})
        url = "%s/reduce?%s" % (server, params)
        print("Reducer is working: ", url)
        reduce_futures.append(http.fetch(url))
    reduce_responses = yield reduce_futures


if __name__ == '__main__':
    IOLoop.current().run_sync(coordinator)