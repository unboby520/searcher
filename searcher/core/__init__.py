#coding:utf8
"""

Global objects collection.

@author: ilcwd
"""
try:
    import ujson as json
except ImportError:
    import json

import logging

import flask

from .exceptions import *
from . import misc
from . import constants, config

# Main application
application = flask.Flask(__name__)

# logger for RPC time cost.
spy_logger = logging.getLogger('searcher.spy')
# logger for request/response (if need).
request_logger = logging.getLogger('searcher.request')

from raven.contrib.flask import Sentry
from searcher.views.middleware import MonitorMiddleware

# Main application
application = flask.Flask(__name__)
sentry = Sentry(dsn = config.sentry_dsn)
middleware = MonitorMiddleware(application, 'searcher', sentry)


_DEFAULT_RESPONSE_HEADERS = {
    "Cache-Control": "no-cache, no-store, must-revalidate",
    "Pragma": "no-cache",
    "Expires": "0",
}

_MIMETYPE_JSON = 'application/json'


def _update_response_headers(resp, headers):
    for k, v in headers.iteritems():
        resp.headers[k] = v


def success_response(content):
    resp = application.response_class(json.dumps(content), mimetype=_MIMETYPE_JSON)
    _update_response_headers(resp, _DEFAULT_RESPONSE_HEADERS)
    return resp, constants.HTTP_STATUS_LINE_OK


def error_response(ex):
    resp = application.response_class(json.dumps(ex), mimetype=_MIMETYPE_JSON)
    _update_response_headers(resp, _DEFAULT_RESPONSE_HEADERS)
    return resp, constants.HTTP_STATUS_LINE_ERROR