# coding:utf8
"""

Author: ilcwd
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import urllib2
import logging
import json


# enable log
_logger = logging.getLogger()
_logger.setLevel(logging.DEBUG)
_logger.addHandler(logging.StreamHandler(stream=sys.stdout))


TEST_URL = os.getenv('TEST_URL', 'http://0.0.0.0:8080')
TEST_TIMEOUT = int(os.getenv('TEST_TIMEOUT', 7))


import werkzeug.test
from wsgiapp import application

client = werkzeug.test.Client(application)


def native_rpc(func, params, timeout=0):
    post = json.dumps(params)
    path = func

    _logger.info("URL: %s", path)
    _logger.debug("POST: %s", post)

    # werkzeug.test.Client donot set REMOTE_ADDR!
    environ_overrides = {'REMOTE_ADDR': '127.0.0.1'}
    resp, status, headers = client.open(path=path, method='POST',
                                        content_type='application/json',
                                        data=post,
                                        environ_overrides=environ_overrides)

    assert status.startswith('2'), (status, )

    result = ''.join(resp)
    _logger.debug("RESULT: %s", result)
    return json.loads(result)


def remote_rpc(func, params, timeout=TEST_TIMEOUT):
    post = json.dumps(params)
    url = TEST_URL + func

    req = urllib2.Request(url, post, {'Content-Type': 'application/json'})
    resp = urllib2.urlopen(req, timeout=timeout)

    _logger.info("URL: %s", url)
    _logger.debug("POST: %s", post)

    try:
        result = json.loads(resp.read())
    except urllib2.HTTPError as e:
        result = e.read()

    _logger.debug("RESULT: %s", result)
    return result

rpc = native_rpc
