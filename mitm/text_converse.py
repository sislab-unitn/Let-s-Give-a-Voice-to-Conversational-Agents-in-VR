import logging
from mitmproxy.log import ALERT
from mitmproxy import http
from http.server import BaseHTTPRequestHandler,HTTPServer
import requests
import datetime
import json
from pprint import pprint
import urllib
from typing import Tuple, Dict
def text_converse(flow : http.HTTPFlow,path : str, port : int, rasa_path : str, rasa_port : int, wit_path : str, wit_port : int, entities:Dict, intents:Dict,traits:Dict) -> Tuple[int,str,Dict]:
    logging.log(ALERT,"Text Converse")
    url = f'http://{rasa_path}:{rasa_port}/webhooks/rest/webhook'
    post_body = flow.request.content
    try: 
        json.loads(post_body)
    except ValueError:
        status_code = 400
        content = "{'Bad Request': 'Invalid JSON'}"
        resp_header = dict(flow.request.headers)
        resp_header['Host'] = rasa_path
        resp_header['Content-Type'] = 'application/json'
        resp_header['Content-Length'] = str(len(content))
        return status_code, content, resp_header
    # post_body = bytes(json.dumps(post_body), 'utf-8')
    req_header = dict(flow.request.headers)
    req_header['Host'] = rasa_path
    req_header['Content-Type'] = 'application/json'
    req_header['Content-Length'] = str(len(post_body))
    resp = requests.post(url, data=post_body, headers=req_header, verify=False)
    if resp.status_code != 200:
        # logging.log(ALERT,resp.content)
        return resp.status_code, resp.content, resp.headers
    # logging.log(ALERT,resp.headers)
    # logging.log(ALERT,resp.content)
    status_code = 200
    return status_code, resp.content, dict(resp.headers)