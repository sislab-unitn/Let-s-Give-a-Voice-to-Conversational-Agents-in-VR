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
# non streamed for now, TODO chunked streaming
def audio_converse(flow : http.HTTPFlow,path : str, port : int, rasa_path : str, rasa_port : int, wit_path : str, wit_port : int, entities:Dict, intents:Dict,traits:Dict) -> Tuple[int,str,Dict]:
    logging.log(ALERT,"Audio Converse")
    
    # audio to text
    url = f'http://{wit_path}:{wit_port}/dictation?v={flow.request.query["v"]}'
    post_body = flow.request.content
    req_header = dict(flow.request.headers)
    resp = requests.post(url, data=post_body, headers=req_header, verify=False)
    if resp.status_code != 200:
        return resp.status_code, resp.content, dict(resp.headers)
    # response is a json array of json objects separated by \r\n
    response_content = resp.content.decode("utf-8").split('\r\n')
    # get the last json object, which is not the last element of the array
    try:
        response_dict = json.loads(response_content[-2])
        text = response_dict["text"]
        logging.log(ALERT,text)
        # ask rasa
        url = f'http://{rasa_path}:{rasa_port}/webhooks/rest/webhook'
        post_body = bytes(json.dumps({"sender": "mitmproxy", "message": text}), 'utf-8')
        req_header = dict(flow.request.headers)
        req_header['Host'] = rasa_path
        req_header['Content-Type'] = 'application/json'
        req_header['Content-Length'] = str(len(post_body))
        try:
            del req_header['Transfer-Encoding']
        except KeyError:
            pass
        resp = requests.post(url, data=post_body, headers=req_header, verify=False)
        if resp.status_code != 200:
            return resp.status_code, resp.content, dict(resp.headers)
        response_dict = json.loads(resp.content.decode("utf-8"))
        text = response_dict[0]["text"]
        logging.log(ALERT,response_dict)
    except IndexError:
        text = "I didn't understand"
    
    # text to audio
    url = f'http://{wit_path}:{wit_port}/synthesize?v={flow.request.query["v"]}'
    post_body = {
                "q": '"'+text + '"',
                "voice": "Rebecca",
                # "style": "soft",
                # "speed": 150,
                # "pitch": 110,
                # "gain": 95
                }
    post_body = bytes(json.dumps(post_body), 'utf-8')
    req_header['Content-Length'] = str(len(post_body))
    req_header['Content-Type'] = 'application/json'
    req_header['Accept'] = 'audio/wav'
    logging.log(ALERT,req_header)
    logging.log(ALERT,post_body)
    resp = requests.post(url, data=post_body, headers=req_header, verify=False)
    logging.log(ALERT,resp.headers)
    if resp.status_code != 200:
        return resp.status_code, resp.content, dict(resp.headers)
    status_code = 200
    return status_code, resp.content, dict(resp.headers)