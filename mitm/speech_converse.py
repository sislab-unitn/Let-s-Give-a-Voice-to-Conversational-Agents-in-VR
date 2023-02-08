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
def speech_converse(flow : http.HTTPFlow, rasa_path : str, rasa_port : int, wit_path : str, wit_port : int, entities:Dict, intents:Dict,traits:Dict) -> Tuple[int,str,Dict]:
    logging.log(ALERT,"Message")
    url = f'http://{rasa_path}:{rasa_port}/model/parse'
    post_body = f'{{"text":"{flow.request.query["q"]}"}}'
    post_body = bytes(post_body, 'utf-8')
    req_header = dict(flow.request.headers)
    req_header['Host'] = rasa_path
    req_header['Content-Type'] = 'application/json'
    req_header['Content-Length'] = str(len(post_body))
    resp = requests.post(url, data=post_body, headers=req_header, verify=False)
    if resp.status_code != 200:
        logging.log(ALERT,resp.content)
        return resp.status_code, resp.content, resp.headers
    # body
    response_dict = resp.json()
    response_body = dict()
    response_body["entities"] = dict()
    used_entities = set()
    for entity in response_dict["entities"]:
        if f'{entity["entity"]}:{entity["entity"]}' not in response_body["entities"]:
            response_body["entities"][f'{entity["entity"]}:{entity["entity"]}'] = list()
        else:
            var = f'{entity["start"]},{entity["end"]},{entity["entity"]},{entity["value"]}'
            logging.log(ALERT,var)
            if var not in used_entities:
                used_entities.add(var)
                response_entity = dict()
                response_entity["body"] = response_dict["text"][entity["start"]:entity["end"]]
                try:
                    response_entity["confidence"] = entity["confidence_entity"]
                except KeyError:
                    response_entity["confidence"] = 1
                response_entity["end"] = entity["end"]
                response_entity["entity"] = dict()
                response_entity["id"] = entities[entity["entity"]]
                response_entity["name"] = entity["entity"]
                response_entity["role"] = entity["entity"]
                response_entity["start"] = entity["start"]
                response_entity["type"] = "value" # to do add dynamic value for intervals and other types
                response_entity["value"] = entity["value"] 
                response_body["entities"][f'{entity["entity"]}:{entity["entity"]}'].append(response_entity)
    response_body["intents"] = list()
    logging.log(ALERT,intents)
    response_dict["intent"]["id"] = intents[response_dict["intent"]["name"]]
    response_body["intents"].append(response_dict["intent"])
    response_body["text"] = response_dict["text"]
    response_body["traits"] = dict()
    # header
    response_header = dict()
    response_header["Content-Type"] = "application/json"
    response_header["Access-Control-Allow-Origin"] = "*"
    response_header["Access-Control-Allow-Headers"] = "*"      
    x = datetime.datetime.now(datetime.timezone.utc)
    response_header["Date"] = x.strftime("%a, %d %b %Y %H:%M:%S GMT")
    response_header["Connection"] = "keep-alive"
    response_header["Content-Length"] = str(len(response_body))
    response_body = json.dumps(response_body,indent=2)
    # status code
    status_code = 200
    return (status_code, response_body, response_header)