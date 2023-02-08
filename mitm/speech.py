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
def speech(flow : http.HTTPFlow, rasa_path : str, rasa_port : int, wit_path : str, wit_port : int, entities:Dict, intents:Dict,traits:Dict) -> Tuple[int,str,Dict]:
    # call dictation
    logging.log(ALERT,flow.request.headers)
    url = f'https://{self.wit_path}:{self.wit_port}/dictation?v={flow.request.query["v"]}'
    post_body = flow.request.content
    headers = dict(flow.request.headers)
    try:
        del(headers['Transfer-encoding'])
    except KeyError:
        pass
    headers['Content-Length'] = str(len(post_body))
    resp = requests.post(url, data=flow.request.content, headers=headers, verify=False)
    response_content = resp.content.decode("utf-8").split('\n}\r\n{\n')
    logging.log(ALERT,response_content)
    # pprint(response_content)
    response_content[0] = response_content[0] + '}'
    for i in range(1,len(response_content)-1):
        response_content[i] = '{' + response_content[i] + '}'
    response_content[-1] = '{' + response_content[-1][:-2]
    logging.log(ALERT,response_content[-1]) 
    response_dict = json.loads(response_content[-1])        
    text = urllib.parse.quote_plus(response_dict["text"])
    logging.log(ALERT,text)
    # call message
    url = f'http://{flow.request.host}/message?v={flow.request.query["v"]}&q={text}'
    req_header = dict(flow.request.headers)
    try: 
        del(req_header['Content-Length'])
    except KeyError:
        pass
    try:
        del(req_header['Content-Type'])
    except KeyError:
        pass
    resp = requests.post(url, headers=req_header, verify=False)
    logging.log(ALERT,resp.headers)
    
    resp_dict = resp.json()
    resp_dict |= response_dict
    status_code = resp.status_code
    return status_code, json.dumps(resp_dict,indent=2), resp.headers