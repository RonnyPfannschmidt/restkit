import threading
from BaseHTTPServer import HTTPServer

import pytest

from .http_server import HTTPTestHandler, HOST, PORT

from restkit.client import Client
from restkit.resource import Resource


@pytest.fixture(scope='session')
def http_server():
    server = HTTPServer((HOST, PORT), HTTPTestHandler)

    server.thread = threading.Thread(target=server.serve_forever)
    server.thread.setDaemon(True)
    server.thread.start()
    return server


@pytest.fixture
def client(http_server):
    return Client(timeout=300)


def fixpath(path):
    if path.startswith("http://") or path.startswith("https://"):
        return path
    else:
        return 'http://%s:%s%s' % (HOST, PORT, path)


@pytest.fixture
def req(client):
    def req(path, *k, **kw):
        return client.request(fixpath(path), *k, **kw)
    req.client = client
    return req


@pytest.fixture
def resource_url(request, http_server):
    try:
        return request.function.markers.url.args[0]
    except AttributeError:
        return 'http://%s:%s' % (HOST, PORT)

@pytest.fixture
def res(resource_url):
    return Resource(resource_url)
