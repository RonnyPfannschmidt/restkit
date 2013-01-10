# -*- coding: utf-8 -
#
# This file is part of restkit released under the MIT license. 
# See the NOTICE for more information.

from __future__ import with_statement

import cgi
import imghdr
import os
import socket
import threading
import Queue
import urlparse
import sys
import tempfile
import time

from restkit.filters import BasicAuth

from .conftest import fixpath

LONG_BODY_PART = "This is a relatively long body, that we send to the client...\n" * 80


def test_base_request(req):
    r = req('/')
    assert r.body_string() == "welcome"


def test_encoded_body(req):
    r = req('/unicode')
    assert r.body_string(charset="utf-8") == u"éàù@"


def test_latin1_url(req):
    r = req(b"/éàù")
    assert r.body_string() == "ok"
    assert r.status_int == 200


def test_content_type(req):
    r = req('/json',
            headers={'Content-Type': 'application/json'})
    assert r.status_int == 200


def test_wrong_content_type(req):
    r = req('/json',
            headers={'Content-Type': 'text/plain'})
    assert r.status_int == 400


def test_response_unknown(req):
    r = req('/unknown',
            headers={'Content-Type': 'application/json'})
    assert r.status_int == 404


def test_query_string(req):
    r = req('/query?test=testing')
    assert r.status_int == 200
    assert r.body_string() == "ok"


def test_response_binary(req, tmpdir):
    r = req('http://e-engura.com/images/logo.gif')
    print r.status
    assert r.status_int == 200
    file = tmpdir.join('logo.gif')
    with file.open('wb') as fp:
        fp.write(r.body_string())
    assert imghdr.what(file.strpath) == 'gif'


def test_response_binary_body_stream(req, tmpdir):
    r = req('http://e-engura.com/images/logo.gif')
    assert r.status_int == 200
    file = tmpdir.join('logo.gif')
    with file.open('w') as fd:
        with r.body_stream() as body:
            for block in body:
                fd.write(block)

    assert imghdr.what(file.strpath) == 'gif'


def test_follow_redirect(client, req):
    client.follow_redirect = True
    r = req('/redirect')
    assert r.status_int == 200
    assert r.body_string() == "ok"
    assert r.final_url == fixpath('/complete_redirect')


def test_post(req):
    r = req('/', 'POST', body="test")
    assert r.body_string() == "test"


def test_post_bytes(req):
    r = req('/bytestring', 'POST', body=b"éàù@")
    assert r.body_string() == "éàù@"


def test_post_unicode(req):
    r = req('/unicode', 'POST', body=u"éàù@")
    assert r.body_string() == "éàù@"


def test_013(req):
    r = req('/json', 'POST', body="test",
            headers={'Content-Type': 'application/json'})
    assert r.status_int == 200

    r = req('/json', 'POST', body="test",
            headers={'Content-Type': 'text/plain'})
    assert r.status_int == 400


def test_014(req):
    r = req('/empty', 'POST', body="",
            headers={'Content-Type': 'application/json'})
    assert r.status_int == 200

    r = req('/empty', 'POST', body="",
            headers={'Content-Type': 'application/json'})
    assert r.status_int == 200


def test_post_with_query(req):
    r = req('/query?test=testing', 'POST', body="",
            headers={'Content-Type': 'application/json'})
    assert r.status_int == 200


def test_body_file(req):
    fn = os.path.join(os.path.dirname(__file__), "1M")
    with open(fn, "rb") as f:
        l = int(os.fstat(f.fileno())[6])
        r = req('/1M', 'POST', body=f)
    assert r.status_int == 200
    assert int(r.body_string()) == l


def test_large(req):
    r = req('/large', 'POST', body=LONG_BODY_PART)
    assert r.status_int == 200
    assert int(r['content-length']) == len(LONG_BODY_PART)
    assert r.body_string() == LONG_BODY_PART


def test_large_often(req):
    for i in range(10):
        test_large(req)


def test_put(req):
    r = req('/', 'PUT', body="test")
    assert r.body_string() == "test"


def test_auth_filter_correct(req, client):
    client.filters = [BasicAuth("test", "test")]
    client.load_filters()
    r = req('/auth')
    assert r.status_int == 200


def test_auth_filter_forbidden(req, client):
    client.filters = [BasicAuth("test", "test2")]
    client.load_filters()
    r = req('/auth')
    assert r.status_int == 403


def test_request_body_list(req):
    lines = ["line 1\n", " line2\n"]
    r = req('/list', 'POST', body=lines,
            headers=[("Content-Length", "14")])
    assert r.status_int == 200
    assert r.body_string() == 'line 1\n line2\n'


def test_chunked_response(req):
    lines = ["line 1\n", " line2\n"]
    r = req('/chunked', 'POST', body=lines,
            headers=[("Transfer-Encoding", "chunked")])
    assert r.status_int == 200
    assert r.body_string() == '7\r\nline 1\n\r\n7\r\n line2\n\r\n0\r\n\r\n'


def test_a_cookie(req):
    r = req('/cookie')
    assert r.cookies.get('fig') == 'newton'
    assert r.status_int == 200


def test_some_cookies(req):
    r = req("/cookies")
    assert r.cookies.get('fig') == 'newton'
    assert r.cookies.get('sugar') == 'wafer'
    assert r.status_int == 200
