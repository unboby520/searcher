#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, with_statement
import json
import threading

import consul
import six


class Client(object):

    def __init__(self, host, port=8500):
        self.consul = consul.Consul(host=host, port=port)
        self._lock = threading.Lock()
        self._values = {}

    def get_str(self, key):
        with self._lock:
            data = self._values.get(key, None)
            if not data:
                _, val = self.consul.kv.get(key)
                data = to_basestring(val['Value'])
                self._values[key] = data
            return data

    def get_json(self, key):
        with self._lock:
            data = self._values.get(key, None)
            if not data:
                _, val = self.consul.kv.get(key)
                data = json_decode(val['Value'])
                self._values[key] = data
            return data


_BASESTRING_TYPES = (six.string_types, type(None))


def json_decode(value):
    return json.loads(to_basestring(value))


def to_basestring(value):
    if isinstance(value, _BASESTRING_TYPES):
        return value
    if not isinstance(value, bytes):
        raise TypeError(
            "Expected bytes, unicode, or None; got %r" % type(value)
        )
    return value.decode("utf-8")


if __name__ == '__main__':
    client = Client('10.10.28.2')
    # print(client.get_str('test'))
    # print(client.get_json('dev/monitor/category'))
    s = client.get_json('dev/service/hotresource/REDIS_CLUSTER_PARAMS')
    print(s)
    print(type(s))
