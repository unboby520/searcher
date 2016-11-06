# coding:utf8
from whoosh import query
from whoosh.query import *
from whoosh.qparser import QueryParser
from whoosh.filedb.filestore import FileStorage
from whoosh import scoring
from whoosh import sorting
from whoosh import collectors
from whoosh.collectors import TermsCollector
from whoosh.collectors import TimeLimitCollector, TimeLimit
from whoosh.qparser import MultifieldParser
import traceback
import sys
reload(sys)
sys.setdefaultencoding('utf8')
from ..models import (config, constants)
from searcher.models import constants
import os
from qiniu import Auth
#import filter
from flask import g

index_video_path = os.path.join(config.index_root_dir, 'video')
storage_video = FileStorage(index_video_path, readonly=True)
ix_video = storage_video.open_index()

index_media_path = os.path.join(config.index_root_dir, 'media')
storage_media = FileStorage(index_media_path, readonly=True)
ix_media = storage_media.open_index()

index_pub_path = os.path.join(config.index_root_dir, 'pub')
storage_pub = FileStorage(index_pub_path, readonly=True)
ix_pub = storage_pub.open_index()

def search_pub(keyword, page, pagelen):
    with ix_pub.searcher() as searcher:
        parser = MultifieldParser(['title', 'pinyin_title'], schema=ix_pub.schema)
        q = parser.parse(keyword)
        results = searcher.search_page(q, pagenum=int(page), pagelen=int(pagelen))
        return constants.CODE_OK, [hit.fields() for hit in results], results.total


def search_video(keyword, page, pagelen):
    with ix_video.searcher() as searcher:
        parser = MultifieldParser(['title', 'pinyin_title'], schema=ix_video.schema)
        q = parser.parse(keyword)
        results = searcher.search_page(q, pagenum=int(page), pagelen=int(pagelen))
        video_list = []
        for hit in results:
            field = hit.fields()
            info = {}
            info['gcid'] = field.get('gcid', '')
            info['movieid'] = field.get('movieid')
            info['uid'] = field.get('uid')
            info['cover_height'] = field.get('cover_height')
            info['cover_width'] = field.get('cover_width')
            info['cover_url'] = field.get('cover_url')
            info['duration'] = field.get('duration')
            info['title'] = field.get('title')
            info['duration'] = field.get('duration')
            video_list.append(info)
            #info['pic'] = field.get('pic')
        return constants.CODE_OK, video_list, results.total


def search_media(keyword, page, pagelen):
    with ix_media.searcher() as searcher:
        parser = MultifieldParser(['title', 'pinyin_title', 'description', 'pinyin_description', 'genres', 'pinyin_genres', 'actor', 'pinyin_actor'], schema=ix_media.schema)
        q = parser.parse(keyword)
        results = searcher.search_page(q, pagenum=int(page), pagelen=int(pagelen))
        return constants.CODE_OK, [hit.fields() for hit in results], results.total

