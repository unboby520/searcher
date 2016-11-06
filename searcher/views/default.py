# coding:utf8
"""

Global/General methods for flask request handler.

Author: ilcwd
"""
import traceback
import logging
import time

from flask import g, request
try:
    # use `ujson` to accelerate serialization
    import ujson as json
except ImportError:
    import json as json

from ..core import application, request_logger, misc, exceptions, error_response
from searcher.core import middleware as mid

_logger = logging.getLogger(__name__)


@application.before_request
def before_request():
    now = time.time()
    g.start_time = time.time()
    g.request_id = misc.generate_request_id(now)
    g.request_args = {}
    g.request_args.update(request.json or {})
    g.request_args.update(request.args or {})
    g.response_status = {}


def _handler_default_exception(ex):
    e = exceptions.APIException(exceptions.errorcode.SERVER_ERROR, extra={'reason': str(ex)})
    return error_response(e.extra)

application.error_handler_spec[None][400] = _handler_default_exception
application.error_handler_spec[None][404] = _handler_default_exception
application.error_handler_spec[None][405] = _handler_default_exception
application.error_handler_spec[None][500] = _handler_default_exception


@application.errorhandler(Exception)
def _handle_service_exception(ex):
    if isinstance(ex, exceptions.BaseServiceException):
        # TODO: add your custom logic
        pass
    else:
        _logger.error("Exception <%s>, Traceback: %r", str(ex), traceback.format_exc())
        ex = exceptions.APIException(exceptions.errorcode.SERVER_ERROR, "server error", extra={'reason': str(ex)})
        mid.on_internal_error()
    return error_response(ex.extra)


@application.teardown_request
def teardown_request(exception=None):
    pass


@application.after_request
def after_request(resp):
    costtime = int((time.time() - g.start_time) * 1000)

    if request.url_rule:
        f = request.url_rule.endpoint
    else:
        f = request.environ['PATH_INFO'][:32]
    msg = dict(
        ct=costtime,
        rid=g.request_id,
        f=f,
    )
    if g.request_args:
        msg['p'] = g.request_args
    if g.response_status:
        msg['r'] = g.response_status

    if resp:
        resp.headers.add("X-Request-Id", g.request_id)

    # log request
    request_logger.info(json.dumps(msg))
    return resp




