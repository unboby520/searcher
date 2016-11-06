#coding:utf8
'''
Created on Oct 25, 2013

@author: ilcwd
'''
from threading import local as threadlocal


''' A threaddict class from web.py ctx
'''
class ThreadedDict(threadlocal):
    """
    Thread local storage.
    
        >>> d = ThreadedDict()
        >>> d.x = 1
        >>> d.x
        1
        >>> import threading
        >>> def f(): d.x = 2
        ...
        >>> t = threading.Thread(target=f)
        >>> t.start()
        >>> t.join()
        >>> d.x
        1
    """
    _instances = set()
    
    def __init__(self):
        ThreadedDict._instances.add(self)
        
    def __del__(self):
        ThreadedDict._instances.remove(self)
        
    def __hash__(self):
        return id(self)
    
    def clear_all():
        """Clears all ThreadedDict instances.
        """
        for t in list(ThreadedDict._instances):
            t.clear()
    clear_all = staticmethod(clear_all)
    
    # Define all these methods to more or less fully emulate dict -- attribute access
    # is built into threading.local.

    def __getitem__(self, key):
        return self.__dict__[key]

    def __setitem__(self, key, value):
        self.__dict__[key] = value

    def __delitem__(self, key):
        del self.__dict__[key]

    def __contains__(self, key):
        return key in self.__dict__

    has_key = __contains__
        
    def clear(self):
        self.__dict__.clear()

    def copy(self):
        return self.__dict__.copy()

    def get(self, key, default=None):
        return self.__dict__.get(key, default)

    def items(self):
        return self.__dict__.items()

    def iteritems(self):
        return self.__dict__.iteritems()

    def keys(self):
        return self.__dict__.keys()

    def iterkeys(self):
        return self.__dict__.iterkeys()

    iter = iterkeys

    def values(self):
        return self.__dict__.values()

    def itervalues(self):
        return self.__dict__.itervalues()

    def pop(self, key, *args):
        return self.__dict__.pop(key, *args)

    def popitem(self):
        return self.__dict__.popitem()

    def setdefault(self, key, default=None):
        return self.__dict__.setdefault(key, default)

    def update(self, *args, **kwargs):
        self.__dict__.update(*args, **kwargs)

    def __repr__(self):
        return '<ThreadedDict %r>' % self.__dict__


# record headers starts with "kp-"
headers = ThreadedDict()
# record fileInfo in commit's
commitInfo = ThreadedDict()
# extra information you want to add to log
extra = ThreadedDict()


def check_and_set_headers(headers, key, value):
    if not headers.has_key(key):
        headers[key] = value


# initial request: clear all global info.
def init_request():
    global headers
    global commitInfo
    global extra
    headers.clear()
    commitInfo.clear()
    extra.clear()