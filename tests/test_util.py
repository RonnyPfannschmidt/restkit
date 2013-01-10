# -*- coding: utf-8 -
#
# This file is part of restkit released under the MIT license. 
# See the NOTICE for more information.


import pytest
from restkit import util


def check_url_encode(input, expected):
    output = util.url_encode(input)
    assert output == expected


def test_urlencode():
    qs = {'a': "a"}
    check_url_encode(qs, "a=a")

    qs = {'a': 'a', 'b': 'b'}
    check_url_encode(qs, "a=a&b=b")
    qs = {'a': 1}
    check_url_encode(qs, "a=1")
    qs = {'a': [1, 2]}
    check_url_encode(qs, "a=1&a=2")
    qs = {'a': [1, 2], 'b': [3, 4]}
    check_url_encode(qs, "a=1&a=2&b=3&b=4")
    qs = {'a': lambda: 1}
    check_url_encode(qs, "a=1")


combinations = [
    (("http://localhost", "/"), "http://localhost/"),
    (("http://localhost/",), "http://localhost/"),
    (("http://localhost/", "/test/echo"), 
        "http://localhost/test/echo"),
    (("http://localhost/", "/test/echo/"), 
        "http://localhost/test/echo/"),
    (("http://localhost", "/test/echo/"),
        "http://localhost/test/echo/"),
    (("http://localhost", "test/echo"), 
        "http://localhost/test/echo"),
    (("http://localhost", "test/echo/"), "http://localhost/test/echo/"),
]

@pytest.mark.parametrize(('params', 'expected'), combinations)
def test_make_uri(params, expected):
    output = util.make_uri(*params)
    assert output == expected
