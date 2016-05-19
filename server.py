#!/usr/bin/python
#
# Flask server, woo!
#

from flask import Flask, request, redirect, url_for, send_from_directory
from flask.ext.cors import CORS, cross_origin

from Queue import Queue

# Setup Flask app.
app = Flask(__name__)
app.debug = True
cors = CORS(app, resources={r"/order": {"origins": "*"}})
app.config['CORS_HEADERS'] = 'Content-Type'

all_snacks = {}
all_snacks['snickers'] = 0
all_snacks['cheetos'] = 1
all_snacks['mandms'] = 2
all_snacks['twix'] = 3
all_snacks['doritos'] = 4
all_snacks['skittles'] = 5

jobQueue = Queue()

class Job:
    def __init__(self, name, location, code):
        self.snacks = {}
        self.name = name
        self.location = location
        self.code = code

    def addSnack(self, id, quantity):
        if quantity > 0:
            self.snacks[id] = quantity

# Routes
@app.route('/')
def root():
  return app.send_static_file('index.html')

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

        qsnickers = request.args.get('snickers', '0')
        qcheetos = request.args.get('cheetos', '0')
        qmandms = request.args.get('mandms', '0')
        qtwix = request.args.get('twix', '0')
        qdoritos = request.args.get('doritos', '0')
        qskittles = request.args.get('skittles', '0')

        print name
        print location
        print str(code)

        job = Job(name, location, code)
        job.addSnack(all_snacks['snickers'], qsnickers)
        job.addSnack(all_snacks['cheetos'], qcheetos)
        job.addSnack(all_snacks['mandms'], qmandms)
        job.addSnack(all_snacks['twix'], qtwix)
        job.addSnack(all_snacks['doritos'], qdoritos)
        job.addSnack(all_snacks['skittles'], qskittles)

        jobQueue.put(job)
        print str(jobQueue.qsize()) + " length"

	return name + " " + location

if __name__ == '__main__':
  app.run(host="unimate.cs.washington.edu", port=int(59595))
