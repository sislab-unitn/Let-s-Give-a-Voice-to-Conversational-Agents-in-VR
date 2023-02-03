from http.server import BaseHTTPRequestHandler,HTTPServer
import argparse, os, random, sys, requests

from socketserver import ThreadingMixIn
import threading


hostname = 'api.wit.ai'

class ProxyHTTPRequestHandler(BaseHTTPRequestHandler):
    protocol_version = 'HTTP/1.1'
    def do_HEAD(self):
        print("HEAD")
        self.do_GET(body=False)
        
    def do_GET(self, body=True):
        print("GET")
        sent = False
        try:
            url = 'https://{}{}'.format(hostname, self.path)
            print(dict(self.headers))
            req_header = dict(self.headers)
            req_header['Host'] = hostname
            print("req_header")
            print(url)
            resp = requests.get(url, headers=req_header, verify=False)
            sent = True

            self.send_response(resp.status_code)
            self.send_resp_headers(resp)
            msg = resp.text
            if body:
                self.wfile.write(msg.encode(encoding='UTF-8',errors='strict'))
            return
        finally:
            if not sent:
                self.send_error(404, 'error trying to proxy GET')

    def do_POST(self, body=True):
        print("POST")
        sent = False
        try:
            url = 'https://{}{}'.format(hostname, self.path)
            content_len = int(self.headers.getheader('content-length', 0))
            post_body = self.rfile.read(content_len)
            
            req_header = dict(self.headers)
            req_header['Host'] = hostname
            
            resp = requests.post(url, data=post_body, headers=req_header, verify=False)
            sent = True

            self.send_response(resp.status_code)
            self.send_resp_headers(resp)
            if body:
                self.wfile.write(resp.content)
            return
        finally:
            if not sent:
                self.send_error(404, 'error trying to proxy POST')

    def send_resp_headers(self, resp):
        respheaders = resp.headers
        print ('Response Header')
        for key in respheaders:
            if key not in ['Content-Encoding', 'Transfer-Encoding', 'content-encoding', 'transfer-encoding', 'content-length', 'Content-Length']:
                print (key, respheaders[key])
                self.send_header(key, respheaders[key])
        self.send_header('Content-Length', len(resp.content))
        self.end_headers()

def parse_args(argv=sys.argv[1:]):
    parser = argparse.ArgumentParser(description='Proxy HTTP requests')
    parser.add_argument('--port', dest='port', type=int, default=9999,
                        help='serve HTTP requests on specified port (default: 9999)')
    parser.add_argument('--hostname', dest='hostname', type=str, default='api.wit.ai',
                        help='hostname to be processd (default: api.wit.ai)')
    args = parser.parse_args(argv)
    return args

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""

def main(argv=sys.argv[1:]):
    global hostname
    args = parse_args(argv)
    hostname = args.hostname
    print('http server is starting on {} port {}...'.format(args.hostname, args.port))
    server_address = ('127.0.0.1', args.port)
    httpd = ThreadedHTTPServer(server_address, ProxyHTTPRequestHandler)
    print('http server is running as reverse proxy')
    httpd.serve_forever()

if __name__ == '__main__':
    main()