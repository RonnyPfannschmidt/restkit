# -*- coding: utf-8 -
#
# This file is part of restkit released under the MIT license. 
# See the NOTICE for more information.

import pytest
pytestmark = [
    pytest.mark.usefixtures('http_server')
]



import os
import uuid
from restkit import request
from restkit.forms import multipart_form_encode

from .conftest import HOST, PORT

LONG_BODY_PART = """This is a relatively long body, that we send to the client...
This is a relatively long body, that we send to the client...
This is a relatively long body, that we send to the client...
This is a relatively long body, that we send to the client...
This is a relatively long body, that we send to the client...
This is a relatively long body, that we send to the client...
This is a relatively long body, that we send to the client...
This is a relatively long body, that we send to the client...
This is a relatively long body, that we send to the client...
This is a relatively long body, that we send to the client...
This is a relatively long body, that we send to the client...
This is a relatively long body, that we send to the client...
This is a relatively long body, that we send to the client...
This is a relatively long body, that we send to the client...
This is a relatively long body, that we send to the client...
This is a relatively long body, that we send to the client...
This is a relatively long body, that we send to the client...
This is a relatively long body, that we send to the client...
This is a relatively long body, that we send to the client...
This is a relatively long body, that we send to the client...
This is a relatively long body, that we send to the client...
This is a relatively long body, that we send to the client...
This is a relatively long body, that we send to the client...
This is a relatively long body, that we send to the client...
This is a relatively long body, that we send to the client...
This is a relatively long body, that we send to the client...
This is a relatively long body, that we send to the client...
This is a relatively long body, that we send to the client...
This is a relatively long body, that we send to the client...
This is a relatively long body, that we send to the client...
This is a relatively long body, that we send to the client...
This is a relatively long body, that we send to the client...
This is a relatively long body, that we send to the client...
This is a relatively long body, that we send to the client...
This is a relatively long body, that we send to the client...
This is a relatively long body, that we send to the client...
This is a relatively long body, that we send to the client...
This is a relatively long body, that we send to the client...
This is a relatively long body, that we send to the client...
This is a relatively long body, that we send to the client...
This is a relatively long body, that we send to the client...
This is a relatively long body, that we send to the client...
This is a relatively long body, that we send to the client...
This is a relatively long body, that we send to the client...
This is a relatively long body, that we send to the client...
This is a relatively long body, that we send to the client...
This is a relatively long body, that we send to the client...
This is a relatively long body, that we send to the client...
This is a relatively long body, that we send to the client...
This is a relatively long body, that we send to the client...
This is a relatively long body, that we send to the client...
This is a relatively long body, that we send to the client...
This is a relatively long body, that we send to the client...
This is a relatively long body, that we send to the client...
This is a relatively long body, that we send to the client..."""


def test_basic():
    u = "http://%s:%s" % (HOST, PORT)
    r = request(u)
    assert r.status_int == 200
    assert r.body_string() == "welcome"


def test_post():
    u = "http://%s:%s" % (HOST, PORT)
    r = request(u, 'POST', body=LONG_BODY_PART)
    assert r.status_int == 200
    body = r.body_string()
    assert len(body) == len(LONG_BODY_PART)
    assert body == LONG_BODY_PART


def test_auth():
    u = "http://test:test@%s:%s/auth" % (HOST, PORT)
    r = request(u)
    assert r.status_int == 200

    u = "http://test:test2@%s:%s/auth" % (HOST, PORT)
    r = request(u)
    assert r.status_int == 403


def test_multipart():
    u = "http://%s:%s/multipart2" % (HOST, PORT)
    fn = os.path.join(os.path.dirname(__file__), "1M")
    f = open(fn, 'rb')
    l = int(os.fstat(f.fileno())[6])
    b = {'a':'aa','b':['bb','éàù@'], 'f':f}
    h = {'content-type':"multipart/form-data"}
    body, headers = multipart_form_encode(b, h, uuid.uuid4().hex)
    r = request(u, method='POST', body=body, headers=headers)
    assert r.status_int == 200
    assert int(r.body_string()) == l


def test_005():
    u = "http://%s:%s/multipart3" % (HOST, PORT)
    fn = os.path.join(os.path.dirname(__file__), "1M")
    f = open(fn, 'rb')
    l = int(os.fstat(f.fileno())[6])
    b = {'a':'aa','b':'éàù@', 'f':f}
    h = {'content-type':"multipart/form-data"}
    body, headers = multipart_form_encode(b, h, uuid.uuid4().hex)
    r = request(u, method='POST', body=body, headers=headers)
    assert r.status_int == 200
    assert int(r.body_string()) == l
    
def test_006():
    u = "http://%s:%s/multipart4" % (HOST, PORT)
    fn = os.path.join(os.path.dirname(__file__), "1M")
    f = open(fn, 'rb')
    content = f.read()
    f.seek(0)
    b = {'a':'aa','b':'éàù@', 'f':f}
    h = {'content-type':"multipart/form-data"}
    body, headers = multipart_form_encode(b, h, uuid.uuid4().hex)
    r = request(u, method='POST', body=body, headers=headers)
    assert r.status_int == 200
    assert r.body_string() == content

def test_007():
    import StringIO
    u = "http://%s:%s/multipart4" % (HOST, PORT)
    content = 'éàù@'
    f = StringIO.StringIO('éàù@')
    f.name = 'test.txt'
    b = {'a':'aa','b':'éàù@', 'f':f}
    h = {'content-type':"multipart/form-data"}
    body, headers = multipart_form_encode(b, h, uuid.uuid4().hex)
    r = request(u, method='POST', body=body, headers=headers)
    assert r.status_int == 200
    assert r.body_string() == content
