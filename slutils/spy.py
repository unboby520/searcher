#coding:utf8
"""
Created on 2012-9-18

@author: ilcwd
"""
import time

DEFAULT_FORMAT = 'func=%s costtime=%dms'


def spy_costtime(logmethod=None, name=None, formatter=DEFAULT_FORMAT):
    """记录函数执行时间开销的装饰器，
    
    Args: 
        logmethod 传入参数是 name, costtime的记录日志方法
        name 如果传入，则使用这个作为函数名，否则使用 func.__name__
    """

    def d(func):        
        def wrapper(*args, **kwargs):
            if logmethod is None:
                return func(*args, **kwargs)
        
            st = time.time()
            try:
                return func(*args, **kwargs)
            finally:
                et = time.time()                
                funcname = (name if name else func.__name__)
                costtime = int((et-st)*1000)
                logmethod(formatter % (funcname, costtime))

        wrapper.__doc__ = func.__doc__
        wrapper.__name__ = func.__name__
        return wrapper
    return d
