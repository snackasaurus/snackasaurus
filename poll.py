#!/usr/bin/python

import server
import time
from threading import Thread

from Queue import Empty

def worker():
    while True:
        try:
            print "waiting for job"
            server.get_job()
            print "got job"

            time.sleep(5)
            print "job was done"
        except KeyboardInterrupt:
            break

worker()
