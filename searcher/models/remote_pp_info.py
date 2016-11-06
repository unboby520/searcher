#-*- coding:utf8 -*-
import requests
from searcher.core import config
from flask import g
from slutils.urltools import PersistentHTTP
import ujson
import functools
import json
import formatURL

TIME_OUT = 3

urlsitter_persistent_http = PersistentHTTP(config.SL_INTER_HOST, TIME_OUT)

def retry(func):
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        output = {}
        status = ''
        for i in xrange(2):
            try:
                status, output = func(self, *args, **kwargs)
                if status:
                    break
            except Exception as e:
                continue
        return status, output
    return wrapper


@retry
def get_pp_info(uid_list):
    url = '/public_user_info/serve/user_info'
    params = {'user_id_list' : uid_list}
    #params = {'gcid_list' : gcid_list, 'peerid' : "123"}
    code, res = urlsitter_persistent_http.url_request(url, ujson.dumps(params), header={'Content-Type': 'application/json'})
    if int(code) != 200:
        return False, None
    res = json.loads(res)
    info_list = res.get('info_list')
    result = []

    for key in info_list.keys():
        value = info_list.get(key)
        info = dict()
        info['kind'] = value.get('kind', 'per')
        if str(value.get('kind', "per")) == 'pub':
            info['icon_url'] =  formatURL.formatPoster(value.get('icon_url'))
        else:
            info['icon_url'] = value.get('icon_url')
        info['uid'] = str(key)
        info['update_count'] = value.get('count')
        info['title'] = value.get('title')
        info['update_time'] = value.get('update_time')
        #info['title'] = str
        info_list[str(key)] = info
    return True, info_list

if __name__ == '__main__':
    print get_pp_info( [586394267])


