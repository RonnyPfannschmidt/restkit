# -*- coding: utf-8 -
#
# This file is part of restkit released under the MIT license
# See the NOTICE for more information.


from restkit.errors import RequestFailed, ResourceNotFound, \
    Unauthorized
from restkit.resource import Resource
from .conftest import HOST, PORT
import pytest


def test_basic(res):
    r = res.get()
    assert r.status_int == 200
    assert r.body_string() == "welcome"


def test_unicode(res):
    r = res.get('/unicode')
    assert r.body_string() == "éàù@"


def test_latin1_path(res):
    r = res.get('/éàù')
    assert r.status_int == 200
    assert r.body_string() == "ok"


def test_unicode_path(res):
    r = res.get(u'/test')
    assert r.status_int == 200
    r = res.get(u'/éàù')
    assert r.status_int == 200


def test_contenttype(res):
    r = res.get('/json',
                headers={'Content-Type': 'application/json'})
    assert r.status_int == 200


def test_contenttype_wrong(res):
    pytest.raises(
        RequestFailed,
        res.get, '/json',
        headers={'Content-Type': 'text/plain'})


def test_not_found(res):
    pytest.raises(ResourceNotFound, res.get, '/unknown')


def test_query_parameters(res):
    r = res.get('/query', test='testing')
    assert r.status_int == 200
    r = res.get('/qint', test=1)
    assert r.status_int == 200


def test_post(res):
    r = res.post(payload="test")
    assert r.body_string() == "test"


def test_post_bytes(res):
    r = res.post('/bytestring', payload=b"éàù@")
    assert r.body_string() == b"éàù@"


def test_post_unicode(res):
    r = res.post('/unicode', payload=u"éàù@")
    assert r.body_string() == "éàù@"

    # another time since its consumed
    r = res.post('/unicode', payload=u"éàù@")
    assert r.body_string(charset="utf-8") == u"éàù@"


def test_post_contenttype(res):
    r = res.post(
        '/json', payload="test",
        headers={'Content-Type': 'application/json'})
    assert r.status_int == 200
    pytest.raises(
        RequestFailed,
        res.post, '/json', payload='test',
        headers={'Content-Type': 'text/plain'})


def test_empty(res):
    # ???
    r = res.post(
        '/empty', payload="",
        headers={'Content-Type': 'application/json'})
    assert r.status_int == 200
    r = res.post('/empty', headers={'Content-Type': 'application/json'})
    assert r.status_int == 200


def test_post_query(res):
    r = res.post('/query', test="testing")
    assert r.status_int == 200


def test_post_payload(res):
    r = res.post('/form', payload={ "a": "a", "b": "b" })
    assert r.status_int == 200


def test_put_payload(res):
    r = res.put(payload="test")
    assert r.body_string() == 'test'


def test_head(res):
    r = res.head('/ok')
    assert r.status_int == 200


def test_delete(res):
    r = res.delete('/delete')
    assert r.status_int == 200


def test_post_filelike(res):
    content_length = len("test")
    import StringIO
    content = StringIO.StringIO("test")
    r = res.post(
        '/json',
        payload=content,
        headers={
            'Content-Type': 'application/json',
            'Content-Length': str(content_length)
        })
    assert r.status_int == 200


def test_post_filelike_contenttype_raises(res):
    import StringIO
    content = StringIO.StringIO("test")
    pytest.raises(
        RequestFailed, res.post, '/json',
        payload=content,
        headers={'Content-Type': 'text/plain'})


def test_auth_in_resource_base():
    u = "http://test:test@%s:%s/auth" % (HOST, PORT)
    res = Resource(u)
    r = res.get()
    assert r.status_int == 200

    u = "http://test:test2@%s:%s/auth" % (HOST, PORT)
    res = Resource(u)
    pytest.raises(Unauthorized, res.get)


def test_multiformvalue(res):
    r = res.post('/multivalueform', payload={"a": ["a", "c"], "b": "b" })
    assert r.status_int == 200


def test_multipart_with_file(res):
    import os
    fn = os.path.join(os.path.dirname(__file__), "1M")
    f = open(fn, 'rb')
    l = int(os.fstat(f.fileno())[6])
    b = {'a': 'aa', 'b': ['bb', 'éàù@'], 'f':f}
    h = {'content-type': "multipart/form-data"}
    r = res.post('/multipart2', payload=b, headers=h)
    assert r.status_int == 200
    assert int(r.body_string()) == l


def test_023(res):
    import os
    fn = os.path.join(os.path.dirname(__file__), "1M")
    f = open(fn, 'rb')
    l = int(os.fstat(f.fileno())[6])
    b = {'a':'aa','b':'éàù@', 'f':f}
    h = {'content-type':"multipart/form-data"}
    r = res.post('/multipart3', payload=b, headers=h)
    assert r.status_int == 200
    assert int(r.body_string()) == l


def test_024(res):
    import os
    fn = os.path.join(os.path.dirname(__file__), "1M")
    f = open(fn, 'rb')
    content = f.read()
    f.seek(0)
    b = {'a':'aa','b':'éàù@', 'f':f}
    h = {'content-type':"multipart/form-data"}
    r = res.post('/multipart4', payload=b, headers=h)
    assert r.status_int == 200
    assert r.body_string() == content


def test_multipart_formdata_stringio(res):
    import StringIO
    content = 'éàù@'
    f = StringIO.StringIO('éàù@')
    f.name = 'test.txt'
    b = {'a': 'aa', 'b': 'éàù@', 'f': f}
    h = {'content-type': "multipart/form-data"}
    r = res.post('/multipart4', payload=b, headers=h)
    assert r.status_int == 200
    assert r.body_string() == content
