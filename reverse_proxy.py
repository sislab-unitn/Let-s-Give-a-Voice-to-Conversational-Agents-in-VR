from http.server import BaseHTTPRequestHandler,HTTPServer
import argparse, sys, requests
from socketserver import ThreadingMixIn
from pprint import pprint

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
            pprint(dict(self.headers))
            req_header = dict(self.headers)
            req_header['Host'] = hostname
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
            pprint(dict(self.headers))
            req_header = dict(self.headers)
            req_header['Host'] = hostname
            post_body = None
            print(url)
            # there are two ways to send post data, either in the body as 1 full packet or in chunks
            # here I handle both cases
            if "Content-Length" in self.headers:
                content_len = int(self.headers["Content-Length"])
                post_body = self.rfile.read(content_len)
                #print(type(post_body))
            elif "chunked" in self.headers.get("Transfer-Encoding", ""):
                post_body = bytearray(b'')
                while True:
                    line = self.rfile.readline().strip()
                    #print(line)
                    chunk_length = int(line, 16)
                    if chunk_length != 0:
                        chunk = self.rfile.read(chunk_length)
                        #print(chunk)
                        post_body += bytearray(chunk)
                    self.rfile.readline() # read and discard the trailing \r\n
                    if chunk_length == 0:
                        post_body = bytes(post_body)
                        break
            print(str(post_body))
            resp = requests.post(url, data=post_body, headers=req_header, verify=False)
            print(resp.content)
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
    print(f'http server is starting on {args.hostname} port {args.port}')
    server_address = ('127.0.0.1', args.port)
    httpd = ThreadedHTTPServer(server_address, ProxyHTTPRequestHandler)
    print('http server is running as reverse proxy')
    httpd.serve_forever()

if __name__ == '__main__':
    main()