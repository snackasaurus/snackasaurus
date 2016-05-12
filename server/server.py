#!/usr/bin/python

import SimpleHTTPServer
import SocketServer

PORT = 8000

Handler = SimpleHTTPServer.SimpleHTTPRequestHandler

httpd = SocketServer.TCPServer(("", PORT), handler)

print "serving at port", PORT
httpd.serve_forever()

