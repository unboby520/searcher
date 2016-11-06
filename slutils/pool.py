#coding:utf8
"""
Created on Jun 6, 2014

Author: ilcwd
"""

from threading import Lock
import time
import logging

__all__ = [
    'Pool',
    'create_factory',
]

EXPIRED_CONNECTION_SECONDS = 180
logger = logging.getLogger(__name__)


class Factory(object):

    def create(self):
        raise NotImplementedError()
    
    def close(self, conn):
        raise NotImplementedError()
    
    
def create_factory(on_create, on_close):
    class _Factory(Factory):
        def create(self):
            return on_create()
        
        def close(self, conn):
            return on_close(conn)
        
    return _Factory()


class PoolItem(object):
    def __init__(self, factory):
        self.lastUsedTime = time.time()
        self.usedCount = 0
        self.createTime = time.time()
        self.factory = factory
        self.conn = None
        
    def get(self):
        if self.conn is None:
            try:
                self.conn = self.factory.create()
            except Exception as e:
                logger.error("fail to create instance[%s]: %s", self.factory, e)
            
            self.createTime = time.time()
            
        self.lastUsedTime = time.time()
        self.usedCount += 1
        return self.conn

    def close(self):
        if self.conn is not None:
            try:
                self.factory.close(self.conn)
            except Exception as e:
                logger.error("fail to close instance[%s]: %s", self.factory, e)
        
        self.conn = None


class _PoolSession(object):
    def __init__(self, pool):
        self.pool = pool
        self.item = pool.get_instance()
    
    def __enter__(self):
        if self.item is not None:
            return self.item.get()
    
    def __exit__(self, type_, value, traceback):
        _ = type_, value, traceback
        if self.item is not None:
            self.pool.return_instance(self.item)
    

class Pool(object):
    def __init__(self, factory, maxSize=10, minSize=None):
        self.factory = factory
        self.size = maxSize
        self.lock = Lock()
        self.instances = []
        for _ in xrange(self.size):
            self.instances.append( PoolItem(self.factory) )
            
    def is_expired(self, item):
        now = time.time()
        if abs(now - item.lastUsedTime) > EXPIRED_CONNECTION_SECONDS:
            return True
        
        return False
        
    def get_instance(self):
        with self.lock:
            if self.instances:
                item = self.instances.pop(0)
                
                # 如果是过期的项目，重新分配一个
                if self.is_expired(item):
                    item.close()
                    logger.info("Expired, reconnect: %s", self.factory)
                    item = PoolItem(self.factory)

                return item
    
    def return_instance(self, item):
        with self.lock:
            self.instances.append(item)
            
    def session(self):
        return _PoolSession(self)


def main():
    import socket
    factory = create_factory(lambda: socket.create_connection(('0.0.0.0', 8080)),
                             lambda c: c.close())

    p = Pool(factory, )
    
    while 1:
        with p.session() as conn:
            print conn
        time.sleep(1)


if __name__ == '__main__':
    main()