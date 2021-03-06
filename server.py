#!/usr/bin/python
#
# Flask server, woo!
#

from flask import Flask, request, redirect, url_for, send_from_directory, jsonify
from flask.ext.cors import CORS, cross_origin

import common
import uuid
from threading import Thread, Lock
from Queue import Queue
from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
from struct import pack
import sys

reload(sys)
sys.setdefaultencoding('utf-8')

# Setup Flask app.
app = Flask(__name__)
app.debug = False
cors = CORS(app, resources={r"/order": {"origins": "*"}})
app.config['CORS_HEADERS'] = 'Content-Type'

all_snacks = {}
all_snacks['snickers'] = 0
all_snacks['cheetos'] = 1
all_snacks['mandms'] = 2
all_snacks['twix'] = 3
all_snacks['doritos'] = 4
all_snacks['skittles'] = 5

SNACK_NAMES = ['snickers', 'cheetos', 'mandms', 'twix', 'doritos', 'skittles']

class Job:
    def __init__(self, name, location, code):
        self.snacks = {}
        self.name = str(name)
        self.location = str(location)
        self.code = code

    def addSnack(self, snack_name, quantity):
        # add the snack IFF the quantity is at least one
        if quantity > 0:
            self.snacks[snack_name] = quantity

    def send_job(self):
        # send the job to the node
        encoded_data = self.encode_data()
        poll_socket = socket(AF_INET, SOCK_STREAM)
        poll_socket.connect(('0.0.0.0', common.POLL_PORT))
        poll_socket.sendall(encoded_data)

    def encode_data(self):
        # encode all of the data to send
        print 'code%d, name:%s, location:%s, number if snacks:%d' % (self.code, self.name, self.location, len(self.snacks))
        result = pack(common.CODE_NAME_LOC_NUM_ENCODING, self.code, self.name, self.location, len(self.snacks))
        for snack_name in self.snacks:
            snack_packed_data = pack(common.SNACK_ENCODING, snack_name, self.snacks[snack_name])
            result = common.combine_structs(result, snack_packed_data)
        return result



# Routes
@app.route('/')
def root():
  return app.send_static_file('index.html')

qLock = Lock()
localJobQueue = Queue()

@app.route('/info')
def info():
    print "{called info}"

    return app.send_static_file('info.html')

@app.route('/display')
def display():
    tempJobs = []

    d = dict() # a=23, b=42, c=[1, 2, 3]

    i = 0
    qLock.acquire()
    while not localJobQueue.empty():
        j = localJobQueue.get()
        tempJobs.append(j)
        d[i] = (j.name, j.location)
        i += 1
    for j in tempJobs:
        localJobQueue.put(j)
    qLock.release()
    print tempJobs
    
    return jsonify(d)

@app.route('/<path:path>')
def static_proxy(path):
  # send_static_file will guess the correct MIME type
  return app.send_static_file(path)

@app.route('/order', methods=['GET', 'POST'])
@cross_origin(origin='*',headers=['Content-Type','Authorization'])
def login():
    global jobQueue

    if request.method == 'GET':
        name = request.args.get('name', '')
        location = request.args.get('location', '')
        code = int(request.args.get('code', ''))

        print name
        print location
        print str(code)

        # create a new job
        job = Job(name, location, code)

        # get any snacks that the user has selected, and put it into the job
        for snack_name in SNACK_NAMES:
            quantity = int(request.args.get(snack_name, '0'))
            job.addSnack(snack_name, quantity)

        # send the job to the poll
        job.send_job()
        print "sent job to poll"
        localJobQueue.put(job)

	return "<b>" + name + "</b> " + location

def getUpdates():
    print "waiting for updates"
    l_socket = socket(AF_INET, SOCK_STREAM)
    l_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    l_socket.bind(('0.0.0.0', common.SERVICE_PORT))
    l_socket.listen(5)

    while True:
        client_socket, client_addr = l_socket.accept()
        recv_data = client_socket.recv(common.BUF_SIZE)
        print "received " + str(recv_data) + " job done"
        
        qLock.acquire()
        job = localJobQueue.get()
        qLock.release()
        print "code " + str(job.code)

if __name__ == '__main__':
    t = Thread(target=getUpdates, args=())
    t.daemon = True
    t.start()

    app.run(host="unimate.cs.washington.edu", port=int(59595))
