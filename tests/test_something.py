# coding: utf8
#
# searcher - test_something
# 
# Author: ilcwd 
# Create: 15/5/11
#


import requests
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import requests
import ujson
import json
from urllib import quote
import hashlib
import hmac
import time
import random
import urllib
from base64 import urlsafe_b64encode

# access_key = 'ios.m.xunlei'
# secret_key = '891bf2eae3b147deff8bc4f85e32d316'
access_key = 'android.m.xunlei'
secret_key = '3c661997dc341cbafa661e7b7dca3d90'
host = 'http://pre.api-shoulei-ssl.xunlei.com'
#host = 'http://api-shoulei-ssl.xunlei.com'
#host = 'http://127.0.0.1:8080'
#access_key = 'frontend.m.xunlei'
#secret_key = '34ac9ddb8cb7c346413e9dd3d036f8a8'

def format_sign(uri, method, payload=None, post=None):
    basestring = '%s&%s&' % (method, quote(uri, safe=''))
    params = sorted(payload.items(), key=lambda d: d[0])
    base_params = "%26".join(['{0}{1}{2}'.format(
        quote(p[0]), '%3D', quote(str(p[1]))) for p in params])
    basestring = basestring + base_params
    print basestring
    if post:
        basestring = basestring + '%26' + ujson.dumps(post)
    #print 111111111111
    #GET&http%3A%2F%2Fpre.api-shoulei-ssl.xunlei.com%2Fivideo%2Finfo&accesskey%3Dios.m.xunlei%26movieid%3D29043340070618112%26nonce%3D93697491%26peerid%3D123%26timestamp%3D1472981077
    #4b9e529cf7444040cf65445eec32c2e804fb8041
    hashed = hmac.new(
        secret_key.encode('utf-8'),
        basestring.encode('utf-8'),
        hashlib.sha1)
    print hashed.hexdigest()

    sign = urlsafe_b64encode(hashed.digest()).decode('utf-8')

    return sign

def test_version():
    global access_key
    global secret_key
    url = host + '/searcher/hot_search'
    payload = {'accesskey': access_key}
    #now = int(time.time())
    now = 1472981077
    nonce = str(random.randint(0, 100000000))
    nonce = 93697491
    payload.update({'timestamp': now, 'nonce': nonce})
    sign = format_sign(url, 'GET', payload)
    url = url + '?accesskey=%s&sig=%s&timestamp=%d&nonce=%s' % (
        access_key, sign, now, nonce)
    print url
    res = requests.get(url)
    print res.text

    access_key = 'frontend.m.xunlei'
    secret_key = '34ac9ddb8cb7c346413e9dd3d036f8a8'

    url = host + '/searcher/all_search'
    payload = {'accesskey': access_key}
    #now = int(time.time())
    now = 1472981077
    nonce = str(random.randint(0, 100000000))
    nonce = 93697491
    payload.update({'timestamp': now, 'nonce': nonce})
    payload.update({'keyword':'test', 'media_size':4, 'pub_size':0, 'video_size':0})
    sign = format_sign(url, 'GET', payload)
    url = url + '?accesskey=%s&sig=%s&timestamp=%d&nonce=%s&keyword=%s&media_size=4&pub_size=0&video_size=0' % (
        access_key, sign, now, nonce, urllib.quote('test'))
    print url
    res = requests.get(url)
    print res.text


    url = host + '/searcher/res_search'
    payload = {'accesskey': access_key}
    #now = int(time.time())
    now = 1472981077
    nonce = str(random.randint(0, 100000000))
    nonce = 93697491
    payload.update({'timestamp': now, 'nonce': nonce})
    payload.update({'keyword':'电影', 'page':1, 'pagelen':8, 'type':'video'})
    sign = format_sign(url, 'GET', payload)
    url = url + '?accesskey=%s&sig=%s&timestamp=%d&nonce=%s&keyword=%s&page=1&pagelen=8&type=video' % (
        access_key, sign, now, nonce, urllib.quote('电影'))
    print url
    res = requests.get(url)
    print res.text


def main():
    test_version()


if __name__ == '__main__':
    main()