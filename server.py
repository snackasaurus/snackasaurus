#!/usr/bin/python
#
# Flask server, woo!
#

from flask import Flask, request, redirect, url_for, send_from_directory
from flask.ext.cors import CORS, cross_origin

# Setup Flask app.
app = Flask(__name__)
app.debug = True
cors = CORS(app, resources={r"/order": {"origins": "*"}})
app.config['CORS_HEADERS'] = 'Content-Type'

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
    if request.method == 'GET':
        name = request.args.get('name', '')
        location = request.args.get('location', '')

	return name + " " + location
if __name__ == '__main__':
  app.run(host="unimate.cs.washington.edu", port=int(59595))
