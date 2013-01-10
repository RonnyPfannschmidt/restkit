# -*- coding: utf-8 -
#
# This file is part of restkit released under the MIT license. 
# See the NOTICE for more information.

import unittest

import webob.exc
from restkit.contrib.webob_helper import wrap_exceptions
from restkit import errors


def test_wrap_exceptions(monkeypatch):
    original = errors.ResourceError
    monkeypatch.setattr(errors, 'ResourceError', None)
    wrap_exceptions()
    assert issubclass(errors.ResourceError, webob.exc.WSGIHTTPException)
    monkeypatch.undo()
    assert errors.ResourceError is original



