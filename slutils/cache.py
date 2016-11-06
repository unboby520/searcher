# coding:utf8
"""

Author: ilcwd
"""
import functools
import logging

from memcache import Client as _mcclient


_logger = logging.getLogger(__name__)


class CacheException(Exception):
    pass


class MCCache(object):

    def __init__(self, servers, logerr=None):
        self.cache = _mcclient(servers=servers, debug=False)
        self.logerr = logerr

    def add(self, key, val=1, time=0):
        try:
            return self.cache.add(key, val, time)
        except Exception as e:
            _logger.warning("Exception during `add`: %s", e)

        return None

    def count(self, key, expires=0, delta=1):
        try:
            result = self.cache.incr(key, delta)
            if result is None:
                self.cache.set(key, delta, expires)
                return delta
            return result
        except Exception as e:
            _logger.warning("Exception during `count`: %s", e)

        return None

    def get(self, key):
        result = None
        try:
            result = self.cache.get(str(key))
        except Exception as e:
            _logger.warning("Exception during `get`: %s", e)

        return result

    def set(self, key, value, expires):
        result = False
        try:
            result = self.cache.set(str(key), value, expires)
        except Exception as e:
            _logger.warning("Exception during `set`: %s", e)

        return result

    def delete(self, key):
        result = False
        try:
            result = self.cache.delete(key)
        except Exception as e:
            _logger.warning("Exception during `del`: %s", e)

        return result


def all_cache_filter(value):
    return True


def not_none_cache_filter(value):
    return value is not None


class CacheContext(object):
    def __init__(self, backend, prefix, cache_filter=not_none_cache_filter, expires=0):
        self.backend = backend
        self.prefix = prefix
        self.cache_filter = cache_filter
        self.expires = expires

    def cacheget(self, func):
        @functools.wraps(func)
        def _wrapper(k):

            key = self.prefix + str(k)
            value = self.backend.get(key)
            if value:
                return value

            value = func(k)
            if self.cache_filter(value):
                self.backend.set(key, value, self.expires)

            return value
        return _wrapper


def main():
    mc = MCCache(['10.0.3.184:11211', '10.0.3.184:11211'])


    mycache = CacheContext(mc, prefix='hehe@')

    @mycache.cacheget
    def hehe(k):
        r = 'hello:' + k
        print "Hehe RPC", r
        return r

    mycache = CacheContext(mc, prefix='haha@')
    @mycache.cacheget
    def haha(a):
        print "Haha RPC"
        return None


    hehe("1")
    hehe("2")
    hehe("3")
    haha("1")
    haha("122")


if __name__ == '__main__':
    main()
