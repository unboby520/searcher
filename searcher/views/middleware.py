#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os
import time

from flask import request_started, request_finished, request, g, jsonify
from prometheus_client import Counter, Histogram, generate_latest
from werkzeug.contrib.fixers import ProxyFix


class MonitorMiddleware(object):

    def __init__(self, flask_app, application_name, sentry, url='/metrics'):
        self.process = os.getpid() - os.getppid()
        flask_app.add_url_rule(url, view_func=metrics, methods=['GET'])
        self.sentry = sentry
        sentry.init_app(flask_app)
        # flask_app.config["RAVEN_IGNORE_EXCEPTIONS"] = [AppError]
        self.wsgi_app = ProxyFix(flask_app.wsgi_app)

        self.req_counter = Counter('%s_requests_total' % application_name,
                                   'Total request counts',
                                   ['method', 'endpoint', 'process'])
        self.err_counter = Counter('%s_error_total' % application_name,
                                   'Total error counts',
                                   ['method', 'endpoint', 'process'])
        self.resp_latency = Histogram('%s_response_latency_millisecond' % application_name,
                                    'Response latency (millisecond)',
                                    ['method', 'endpoint', 'process'],
                                    buckets=(10, 20, 30, 50, 80, 100, 200, 300, 500, 1000, 2000, 3000))

        request_started.connect(self._log_request, flask_app)
        request_finished.connect(self._log_response, flask_app)

    def internal_server_error(self, e):
        # TODO: logging error
        self.on_internal_error(e)
        return jsonify({
            'status_code': 500, 'err_msg': 'Internal server error.'
        })

    def on_internal_error(self):
        self.err_counter.labels(self._label()).inc()
        self.sentry.captureException()

    def __call__(self, environ, start_response):
        return self.wsgi_app(environ, start_response)

    def _label(self):
        return {
                'method': request.method,
                'endpoint': request.url_rule.rule,
                'process': self.process
            }

    def _log_request(self, sender, **extra):
        if request.url_rule:
            g._request_start_time = time.time()

    def _log_response(self, sender, response, **extra):
        if not hasattr(g, '_request_start_time') or\
                response.mimetype not in ['application/json', 'text/html']:
            return

        if not request.url_rule:
            return

        label = self._label()
        time_used = int((time.time() - g._request_start_time) * 1000)
        self.req_counter.labels(label).inc()
        self.resp_latency.labels(label).observe(time_used)


def metrics():
    data = generate_latest()
    return data, 200, {'Content-Type': 'text/plain; charset=utf-8'}