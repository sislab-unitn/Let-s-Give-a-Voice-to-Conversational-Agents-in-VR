"""
Basic skeleton of a mitmproxy addon.
Add this intercepter to every mitmproxy instance to get the latency of the request
Run as follows: mitmproxy -s anatomy.py
"""
import logging
from mitmproxy.log import ALERT
from mitmproxy import http
from http.server import BaseHTTPRequestHandler,HTTPServer
import argparse, sys, requests, datetime
import json
from pprint import pprint
from typing import Tuple, Dict
class Injector:
    def __init__(self):
        self.time = None
        pass
    
    def request(self, flow : http.HTTPFlow):
        self.time = datetime.datetime.now().timestamp()
        # add header timestamp
        
        
    def response(self, flow : http.HTTPFlow):
        flow.response.headers["custom_time_stamp"] = str(datetime.datetime.now().timestamp() - self.time)
addons = [Injector()]