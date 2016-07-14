#!/usr/bin/python
# -*- coding: utf8 -*-


import BaseHTTPServer


class MyHttpRequestHandle(BaseHTTPServer.BaseHTTPRequestHandler):

    def do_GET(self):
        self.wfile.write('<html><head><title>python</title></head><body><h2>'
                         'This is a simple python server</h2></body></html>')

server_addr = ('', 8000)
httpd = BaseHTTPServer.HTTPServer(server_addr, MyHttpRequestHandle)
httpd.serve_forever()
