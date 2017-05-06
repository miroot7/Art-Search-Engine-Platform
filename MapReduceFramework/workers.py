#!/use/bin/env python3

import tornado
from tornado.ioloop import IOLoop
from tornado import web, httpserver, httpclient
from tornado import process, netutil
import socket
import json
import logging
from MapReduceFramework import inventory, coordinator, mapper, reducer


log = logging.getLogger(__name__)


def startWorkers():
    task_id = process.fork_processes(inventory.NUM_WORKER, max_restarts=0)
    port = inventory.BASE_PORT + task_id
    app = httpserver.HTTPServer(
        web.Application([web.url(r"/map", mapper.MapHandler),
        web.url(r"/retrieve_map_output", mapper.RetrieveMapOutputHandler),
        web.url(r"/reduce", reducer.ReduceHandler)]))
    log.info("Worker %d is listening on %d", task_id, port)
    
    app.add_sockets(netutil.bind_sockets(port))
    IOLoop.current().start()


if __name__ == "__main__":
    logging.basicConfig(format='%(levelname)s - %(asctime)s - %(message)s', level=logging.DEBUG)
    startWorkers()
