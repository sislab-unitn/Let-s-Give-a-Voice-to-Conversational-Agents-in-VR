from __future__ import absolute_import
import sys
from twisted.internet import reactor
from twisted.web import proxy, server
from twisted.python import log
from twisted.python.compat import urllib_parse, urlquote
from twisted.web.resource import Resource
from twisted.web.server import NOT_DONE_YET
class GenericReverseProxyResource(Resource):
    """
    Resource that renders the results gotten from another server
    Put this resource in the tree to cause everything below it to be relayed
    to a different server.
    @ivar proxyClientFactoryClass: a proxy client factory class, used to create
        new connections.
    @type proxyClientFactoryClass: L{ClientFactory}
    @ivar reactor: the reactor used to create connections.
    @type reactor: object providing L{twisted.internet.interfaces.IReactorTCP}
    """
    proxyClientFactoryClass = proxy.ProxyClientFactory
    def __init__(self, path, reactor=reactor):
        """
        @param path: the base path to fetch data from. Note that you shouldn't
            put any trailing slashes in it, it will be added automatically in
            request. For example, if you put B{/foo}, a request on B{/bar} will
            be proxied to B{/foo/bar}.  Any required encoding of special
            characters (such as " " or "/") should have been done already.
        @type path: C{str}
        """
        Resource.__init__(self)
        self.path = path
        self.reactor = reactor
    def getChild(self, path, request):
        """
        Create and return a proxy resource with the same proxy configuration
        as this one, except that its path also contains the segment given by
        C{path} at the end.
        """
        return GenericReverseProxyResource(self.path + b'/' + urlquote(path, safe=b"").encode('utf-8'),self.reactor)
    def render(self, request): 
        """
        Render a request by forwarding it to the proxied server.
        """
        host = request.getHeader(b'proxy-host')
        port = request.getHeader(b'proxy-port') or 80
        # RFC 2616 tells us that we can omit the port if it's the default port,
        # but we have to provide it otherwise
        if port != 80:
            host += u":" + str(port)
        request.requestHeaders.setRawHeaders(b"host", [host.encode('ascii')])
        request.content.seek(0, 0)
        qs = urllib_parse.urlparse(request.uri)[4]
        if qs:
            rest = self.path + b'?' + qs
        else:
            rest = self.path
        clientFactory = self.proxyClientFactoryClass(
        request.method, rest, request.clientproto,
        request.getAllHeaders(), request.content.read(), request)
        self.reactor.connectTCP(host, port, clientFactory)
        return NOT_DONE_YET
log.startLogging(sys.stdout)
site = server.Site(GenericReverseProxyResource(path='api.wit.ai'))
reactor.listenTCP(8080, site)
reactor.run()