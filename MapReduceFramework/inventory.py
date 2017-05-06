#!/use/bin/env python3

import hashlib, getpass
import socket


NUM_WORKER = 4

MAX_PORT = 49152
MIN_PORT = 10000
BASE_PORT = int(hashlib.md5(getpass.getuser().encode()).hexdigest()[:8], 16) % \
    (MAX_PORT - MIN_PORT) + MIN_PORT 


BASE_PORT += 20

host = "http://127.0.0.1:"
workerServers = [host + str(BASE_PORT + n) for n in range(NUM_WORKER)]