#!/usr/bin/python
#
# Flask server, woo!
#

from flask import Flask, request, redirect, url_for, send_from_directory

# Setup Flask app.
app = Flask(__name__)
app.debug = True


# Routes
@app.route('/')
def root():
  return app.send_static_file('index.html')

@app.route('/<path:path>')
def static_proxy(path):
  # send_static_file will guess the correct MIME type
  return app.send_static_file(path)

@app.route('/order', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        name = request.args.get('name', '')
        location = request.args.get('location', '')

	return name + " " + location
if __name__ == '__main__':
  app.run(port=int(59595))
