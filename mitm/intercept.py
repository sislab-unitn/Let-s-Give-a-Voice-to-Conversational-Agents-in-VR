"""
Basic skeleton of a mitmproxy addon.

Run as follows: mitmproxy -s anatomy.py
"""
import logging
from mitmproxy.log import ALERT
from mitmproxy import http
from http.server import BaseHTTPRequestHandler,HTTPServer
import argparse, sys, requests, datetime
import json
from pprint import pprint
import urllib

from message import message
from speech import speech
from event import event
from converse import converse
from text_converse import text_converse
from audio_converse import audio_converse

from typing import Tuple, Dict
class Injector:
    def __init__(self):
        self.path = "127.0.0.1"
        self.rasa_path = "127.0.0.1"
        self.wit_path = "127.0.0.1"
        self.port = 8080
        self.rasa_port = 8082
        self.wit_port = 8081
        self.entities = dict()
        self.intents = dict()
        self.traits = dict()
        self.ids = False
    def __request_id__(self,host,token:str):
        # get intents
        req_header = {"Authorization":token}
        logging.log(ALERT,req_header)
        url = f'https://{host}/intents'
        resp = requests.get(url,headers=req_header, verify=False)
        self.intents = {intent["name"]:intent["id"] for intent in list(resp.json())}
        # get entities
        url = f'https://{host}/entities'
        resp = requests.get(url,headers=req_header, verify=False)
        self.entities = {entity["name"]:entity["id"] for entity in list(resp.json())}
        # get traits
        url = f'https://{host}/traits'
        resp = requests.get(url,headers=req_header, verify=False)
        self.traits = {trait["name"]:trait["id"] for trait in list(resp.json())}
        self.ids = True
        # logging.log(ALERT,self.intents)
        # logging.log(ALERT,self.entities)
        # logging.log(ALERT,self.traits)
    def request(self, flow : http.HTTPFlow):
        if not self.ids:
            self.__request_id__(flow.request.host,flow.request.headers["Authorization"])
        logging.log(ALERT,flow.request)
        logging.log(ALERT,flow.request.path)
        if flow.request.path.startswith('/message'):
            status_code, response_body, response_header = message(flow,self.path,self.port,self.rasa_path,self.rasa_port,self.wit_path,self.wit_port,self.entities,self.intents,self.traits)
            flow.response = http.Response.make(status_code = status_code, content = response_body, headers = response_header)
        # if flow.request.path.startswith('/speech'):
        #     status_code, response_body, response_header = speech(flow,self.path,self.port,self.rasa_path,self.rasa_port,self.wit_path,self.wit_port,self.entities,self.intents,self.traits)
        #     flow.response = http.Response.make(status_code = status_code, content = response_body, headers = response_header)
        if flow.request.path.startswith('/event'):
            status_code, response_body, response_header = event(flow,self.path,self.port,self.rasa_path,self.rasa_port,self.wit_path,self.wit_port,self.entities,self.intents,self.traits)
            flow.response = http.Response.make(status_code = status_code, content = response_body, headers = response_header)
        if flow.request.path.startswith('/converse'):
            status_code, response_body, response_header = converse(flow,self.path,self.port,self.rasa_path,self.rasa_port,self.wit_path,self.wit_port,self.entities,self.intents,self.traits)
            flow.response = http.Response.make(status_code = status_code, content = response_body, headers = response_header)
        if flow.request.path.startswith('/text_converse'):
            status_code, response_body, response_header = text_converse(flow,self.path,self.port,self.rasa_path,self.rasa_port,self.wit_path,self.wit_port,self.entities,self.intents,self.traits)
            flow.response = http.Response.make(status_code = status_code, content = response_body, headers = response_header)
        if flow.request.path.startswith('/audio_converse'):
            status_code, response_body, response_header = audio_converse(flow,self.path,self.port,self.rasa_path,self.rasa_port,self.wit_path,self.wit_port,self.entities,self.intents,self.traits)
            flow.response = http.Response.make(status_code = status_code, content = response_body, headers = response_header)
        # change the host here if i want to redirect the request
        # flow.request.host = "mitmproxy.org"
        #logging.log(ALERT,flow.request.content)
        #logging.log(ALERT,flow.request.headers)
    def response(self, flow : http.HTTPFlow):
        pass
addons = [Injector()]