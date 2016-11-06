#coding:utf8 
#__author__ = 'xiaobei'
#__time__= '5/24/16'
import requests
from searcher.core import config
from flask import g
from slutils.urltools import PersistentHTTP
import ujson
import functools

TIME_OUT = 3

urlsitter_persistent_http = PersistentHTTP(config.URLSITTER_HOST, TIME_OUT)


def retry(func):
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        res = None
        for i in xrange(3):
            try:
                res = func(self, *args, **kwargs)
                if res:
                   break
            except Exception as e:
                continue
        return res
    return wrapper


@retry
def geturl(gcid_list):
    url = config.URLSITTER_URI
    params = {'gcid_list' : gcid_list, 'peerid' : g.guid}
    #params = {'gcid_list' : gcid_list, 'peerid' : "123"}
    code, res = urlsitter_persistent_http.url_request(url, ujson.dumps(params), header={'Content-Type': 'application/json'})
    if code == 200:
        res = ujson.loads(res)
        play_url = res['playurl']
        return play_url
    else:
        return None


@retry
def geturl_v2(gcid_list):
    url = 'urlsitter/formaturl_v2'
    #params = {'gcid_list' : gcid_list, 'peerid' : g.guid}
    params = {'gcid_list' : gcid_list, 'peerid' : ""}
    code, res = urlsitter_persistent_http.url_request(url, ujson.dumps(params), header={'Content-Type': 'application/json'})
    if code == 200:
        res = ujson.loads(res)
        return res.get('url_info')
    else:
        return None


if __name__ == '__main__':
    #g.peer_id='aSSDAFDS'
    print geturl_v2([u'1f50757939f4fac6dadb57da8cf8df2df6448cad'])
