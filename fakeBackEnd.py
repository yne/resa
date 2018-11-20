#!/usr/bin/env python
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from SimpleHTTPServer import SimpleHTTPRequestHandler
import os
import ssl

class Handler(SimpleHTTPRequestHandler):
    index="index.html"
    def do_GET(self):
        if "api" not in self.path and not os.path.exists(self.path.lstrip('/').split("?")[0]):
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
    cert = './server.pem' # openssl req -new -x509 -keyout server.pem -out server.pem -days 365 -nodes
    secu = os.path.isfile(cert)
    httpd = HTTPServer((host, port), Handler)
    if secu: httpd.socket = ssl.wrap_socket (httpd.socket, certfile=cert, server_side=True)
    print('Serving http%s://%s:%d ...' % ("s" if secu else "", host, port))
    httpd.serve_forever()

