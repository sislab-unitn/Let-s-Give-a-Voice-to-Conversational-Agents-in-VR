"""
Basic skeleton of a mitmproxy addon.

Run as follows: mitmproxy -s anatomy.py
"""
import logging
from mitmproxy import http

class Counter:
    def __init__(self):
        self.num = 0

    def request(self, flow : http.HTTPFlow):
        print(flow.request)
        print(flow.request.headers)
        print(flow.request.content)
        print(flow.response)

addons = [Counter()]