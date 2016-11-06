# coding:utf8
#__author__ = 'xiaobei'
#__time__= '11/16/15'

import traceback
import sys
reload(sys)
sys.setdefaultencoding('utf8')
from searcher.models import constants
import random
import hashlib

from qiniu import Auth
#import filter
from flask import g


def formatPoster(pic):
    return '%s%s' % (constants.QINIU_PIC_URI, pic)


def gen_poster_url(movieid, type, width, height):
    host = 'http://i%d.media.geilijiasu.com' % random.randrange(start=0, stop=3)
    m = hashlib.md5()
    m.update('%s_%dx%d' % (str(movieid), int(width), int(height)))
    md5_str = m.hexdigest()
    return '%s/%s/%s/%s/%s.jpg' % (host, str(type), md5_str[0:2], md5_str[2:4], md5_str)

from slutils.urltools import curl

if __name__ == '__main__':
    #[u'9cf9697cddae101e484bdba7230a36f83baf1705']

    gcid = {'gcid' :u'9cf9697cddae101e484bdba7230a36f83baf1705'}

    # status, output = curl.openurl(url)
    #
    # print upload('7dca38f089a04352bc08c20589ea4fe4c04f02ba', output)
    # print formatPoster('7dca38f089a04352bc08c20589ea4fe4c04f02ba')

    # f = open('/root/text.jpg', 'w+b')
    # f.write(output)
    # f.close
    # print output
    # print formatURL('3039c761468b857649a9f70a28a5f266e9d4fdee')
    # gcid=[{'gcid' : '009cc65526474a64b809e9cc5abdfa32abccb4e8'}, {'gcid' : '006f37168a85735b8432102f72b807dfac061a7d'}]
    # print batchFormatUrls(gcid)
