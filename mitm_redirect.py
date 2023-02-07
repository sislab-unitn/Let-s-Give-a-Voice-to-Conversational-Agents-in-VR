import mitmproxy
from mitmproxy.models import HTTPResponse
from netlib.http import Headers
def request(flow):
    if flow.request.url == 'http://google.com/accounts/':
        flow.request.host = 'stackoverflow.com'
        flow.request.path = '/users/'