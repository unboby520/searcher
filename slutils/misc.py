#coding:utf8

import datetime
import random
import struct
import socket
import time
from collections import deque

TIME_FORMAT = '%Y-%m-%d %H:%M:%S'
STRING_ENCODING = 'utf8'


def ip2Int(ip):    
    return struct.unpack("!I", socket.inet_aton(ip))[0]


def int2Ip(i):
    return socket.inet_ntoa(struct.pack("!I", i))


def toStr(obj):
    """Python Object to str."""
    if isinstance(obj, unicode):
        return obj.encode(STRING_ENCODING)
    
    return str(obj)


def now():
    return datetime2str(datetime.datetime.now())


def datetime2str(t):
    return t.strftime(TIME_FORMAT)


def timestamp2str(ts):
    return datetime2str(datetime.datetime.fromtimestamp(ts))


def str2datetime(dstr):
    return datetime.datetime.strptime(dstr, TIME_FORMAT)


def str2timestamp(s):
    return time.mktime(time.strptime(s, TIME_FORMAT))


def memodict(f):
    """ Memoization decorator for a function taking a single argument """
    class Memodict(dict):
        def __missing__(self, key):
            ret = self[key] = f(key)
            return ret 
    return Memodict().__getitem__


def randomStr(n=16):
    """generate a SHORT random string include digits and letters.
    """
    SAMPLE = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    return ''.join([random.choice(SAMPLE) for _i in xrange(n)])


def randomInt(n=10):
    SAMPLE = '0123456789'
    return ''.join([random.choice(SAMPLE) for _i in xrange(n)])


class LimitedNumericQueue(object):
    """FIFO queue with limited length.
    """
    def __init__(self, n):
        self._n = 0
        self._max = int(n)
        self._queue = deque()
        self._sum = 0.0
        
    def add(self, item):
        if self._max >= self._n:
            t1 = self._queue.popleft()
            self._sum -= t1
        else:
            self._n += 1    
        
        self._queue.append(item)
        self._sum += item
        
    def avg(self):
        """ 
        Only for numeric elements.
        """
        return self._sum / (self._n + 1)


class BackEndManager(object):
    def __init__(self, host, n, timeouts_min, timeouts_avg, timeouts_max):
        assert timeouts_min < timeouts_avg < timeouts_max, "Timeouts must be in ascending order."
        
        self.queue = LimitedNumericQueue(n)
        self._to_min = timeouts_min
        self._to_avg = timeouts_avg
        self._to_max = timeouts_max
        self._host = host
        
    def _timeout(self):
        """max handling time this request should perform."""
        return max(self._to_min, self._to_max-self.queue.avg())
    
    def addResponseTime(self, t):
        """Record this handling time cost."""
        self.queue.add(t)
        
    def hostAndTimeout(self):
        return self._host, self._timeout()


def main():
    print randomStr(16)

if __name__ == '__main__':
    main()