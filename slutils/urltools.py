#coding:UTF-8

from threading import local
import threading
import pycurl
import requests
try:
    import cStringIO
    import pycurl
except ImportError:
    enable_pycurl = False
else:
    enable_pycurl = True



def utf8(o):
    if isinstance(o, unicode):
        return o.encode('utf8')
    return o

class PyCurl(local):
    
    def __init__(self, encoding='utf8'):
        self.encoding=encoding
    
    def openurl(self, url, postdata = None, header=None, timeout=8):
        buf = cStringIO.StringIO()
        c = pycurl.Curl()
        
        c.setopt(pycurl.URL, url)
        c.setopt(pycurl.WRITEFUNCTION, buf.write)
        c.setopt(pycurl.CONNECTTIMEOUT, timeout)
        c.setopt(pycurl.TIMEOUT, timeout)
    
        temp_header = {'Expect': ''}
        if header:
            temp_header.update(header)
            
        headerlist = []
        for k, v in temp_header.iteritems():
            item = '%s: %s' % (k, v)
            if isinstance(item, unicode):
                item = item.encode(self.encoding)
            headerlist.append(item)
            
        c.setopt(pycurl.HTTPHEADER, headerlist)
    
        if postdata:
            if isinstance(postdata, unicode):
                c.setopt(pycurl.POSTFIELDS, postdata.encode(self.encoding))
            else:
                c.setopt(pycurl.POSTFIELDS, postdata)
    
        try:
            c.perform()
            code = c.getinfo(pycurl.RESPONSE_CODE)
            ret =  buf.getvalue()
            return int(code), ret
        except pycurl.error, e:
            return 599, str(e)
        except Exception, e:
            return 598, str(e)
        finally:
            c.close()
            
import urllib2   
class UrlCurl(local):
    
    def __init__(self, encoding='utf8'):
        self.encoding=encoding
    
    def openurl(self, url, postdata = None, header=None, timeout=8):
        if header is None: header = {}
        
        req = urllib2.Request(url, postdata, header)
        
        try:
            resp = urllib2.urlopen(req, timeout=timeout)
            code = resp.getcode()
            result = resp.read()
        except urllib2.HTTPError as e:
            code = e.getcode()
            result = e.read()
        except Exception, e:
            code, result = 598, str(e)
        
        return code, result


class RequestsCurl(local):
    def __init__(self, encoding='utf8'):
        self.encoding = encoding

    def openurl(self, url, type, headers=None, jsondata=None, timeout=1):
        if headers is None:
            headers = {}
        if type == 'get':
            res = requests.get(url, timeout=timeout)
        elif type == 'post':
            res = requests.post(
                url,
                data=jsondata,
                headers=headers,
                timeout=timeout)
        elif type == 'patch':
            res = requests.patch(
                url,
                data=jsondata,
                headers=headers,
                timeout=timeout)
        elif type == 'delete':
            res = requests.delete(url, timeout=timeout)

        try:
            code = res.status_code
            resp_json = res.json()
        except Exception as e:
            code, resp_json = 598, str(e)

        return code, resp_json
        
# 兼容各种
if enable_pycurl:
    curl = PyCurl()
else:
    curl = UrlCurl()

requestCurl = RequestsCurl()

class PersistentHTTP(object):

    def __init__(self, host, timeout):
        self.host = utf8(host)
        self.timeout = timeout
        self.default_headers = {
            'Expect': '',
        }
        self.contexts = {}
        self.default_headers['Connection'] = 'Keep-Alive'
        self.default_headers['Keep-Alive'] = '300'


    def close_connections(self):
        c = self.contexts
        self.contexts = {}
        try:
            for _, v in c.iteritems():
                v.close()
        except Exception as _e:
            pass


    def get_connection(self):
        pid = threading.current_thread().ident
        conn = self.contexts.get(pid)
        if not conn:
            conn = pycurl.Curl()
            self.contexts[pid] = conn

        return conn

    def url_request(self, url, postdata = None, header = None, timeout=None):
        buf = cStringIO.StringIO()

        context = self.get_connection()
        context.setopt(pycurl.URL, self.host + url)
        context.setopt(pycurl.WRITEFUNCTION, buf.write)

        if not timeout:
            timeout = self.timeout

        context.setopt(pycurl.CONNECTTIMEOUT, timeout)
        context.setopt(pycurl.TIMEOUT, timeout)

        t_header = self.default_headers.copy()
        headerlist = []
        if header:
            t_header.update(header)

        for k, v in t_header.iteritems():
            item = '%s: %s' % (k, v)
            if isinstance(item, unicode):
                item = item.encode('utf-8')
            headerlist.append(item)

        context.setopt(pycurl.HTTPHEADER, headerlist)

        if postdata:
            if isinstance(postdata, unicode):
                context.setopt(pycurl.POSTFIELDS, postdata.encode('utf-8'))
            else:
                context.setopt(pycurl.POSTFIELDS, postdata)

        try:
            context.perform()
            code = context.getinfo(pycurl.RESPONSE_CODE)
            return code, buf.getvalue()
        except Exception as e:
            self.close_connections()
            return 599, None
        finally:
            buf.close()



if __name__ == '__main__':
    url = 'http://192.168.10.201/sxsvr/login'
    print curl.openurl(url, postdata='XSVR1111111',header={'v':4})
    
    