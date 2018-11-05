#!/usr/bin/env python
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from SimpleHTTPServer import SimpleHTTPRequestHandler
import os

class Handler(SimpleHTTPRequestHandler):
    index="index.html"
    def do_GET(self):
        if not self.path.lstrip('/'):
            self.path = '/'
        return SimpleHTTPRequestHandler.do_GET(self)
    def do_POST(self):
        payload = self.rfile.read(int(self.headers['Content-Length']))
        print(payload)
        return self.do_GET()
    def do_HEAD(self):
        f = open(self.index, 'rb')
        self.send_response(200)
        self.send_header("Last-Modified", self.date_time_string(os.fstat(f.fileno()).st_mtime))
        self.send_header("Content-Length", str(os.fstat(f.fileno())[6]))
        self.end_headers()
        if f:
            f.close()

if __name__ == "__main__":
    from sys import argv
    host = '0.0.0.0'
    port = int(argv[1]) if len(argv) == 2 else 8000
    print('Serving http://%s:%d ...' % (host, port))
    HTTPServer((host, port), Handler).serve_forever()

