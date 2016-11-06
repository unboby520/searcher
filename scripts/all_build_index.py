#-*- coding:utf8 -*-
from __future__ import unicode_literals
from pypinyin import lazy_pinyin
from whoosh.index import open_dir
from whoosh.index import create_in
from whoosh.index import exists_in
from whoosh.fields import Schema, STORED, ID, KEYWORD, TEXT, DATETIME, NUMERIC
from whoosh.query import *
from whoosh import query
from whoosh.qparser import QueryParser
from whoosh.filedb.filestore import FileStorage
from whoosh import scoring
import os.path
from whoosh import sorting
from datetime import datetime
from datetime import timedelta
from whoosh import writing
from whoosh import qparser
from whoosh import collectors
from whoosh.collectors import TermsCollector
from whoosh.collectors import TimeLimitCollector, TimeLimit
import sys
sys.path.append('/data/apps/searcher/current')
from apscheduler.schedulers.blocking import BlockingScheduler
import sys
from slutils.urltools import requestCurl
import json
import time
import hashlib
from urllib import unquote
from searcher.models import config
from slutils import mysql_new
import os
import datetime
from searcher.models import formatURL
from whoosh.analysis import RegexAnalyzer
from whoosh.analysis import StandardAnalyzer
from jieba.analyse import ChineseAnalyzer
from whoosh.analysis import LanguageAnalyzer
from jieba.analyse import ChineseAnalyzer
from collections import defaultdict
analyzer_zhongwen = ChineseAnalyzer()
analyzer_pinyin = RegexAnalyzer()

def pub_rebuild():
    print datetime.datetime.now()
    print 'pub_rebuild'
    pub_db = mysql_new.BaseDB(config.MYSQL_DEFINE_PUB)
    schema = Schema(uid = ID(stored=True, unique=True),
                title=TEXT(stored=True, analyzer=analyzer_zhongwen),
                pinyin_title = TEXT(stored=True, analyzer=analyzer_pinyin),
                icon_url=ID(stored=True),
                description=STORED,
                v_status=NUMERIC(stored=True),
                )
    SQL = '''SELECT `uid`, `title`, `icon_url`, `description`, `v_status` FROM `pp_category_info`
          '''
    res = pub_db.query(SQL, ())
    if not res:
        return
    index_path = os.path.join(config.index_root_dir, 'pub')
    if not os.path.exists(index_path):
        os.mkdir(index_path)
    #ix = create_in(index_path, schema=schema)
    storage = FileStorage(index_path)
    ix = storage.open_index()
    writer = ix.writer()

    for info in res:
        if not str(info.get('icon_url')).strip():
            continue
        info['icon_url'] = formatURL.formatPoster(info.get('icon_url'))
        pinyin_title = ' '.join(lazy_pinyin(info.get('title').decode('utf8')))
        writer.add_document(uid = str(info.get('uid')).decode('utf8'),
                            title = info.get('title').decode('utf8'),
                            pinyin_title = pinyin_title,
                            icon_url = info.get('icon_url').decode('utf8'),
                            description = info.get('description').decode('utf8'),
                            v_status = info.get('v_status')
                            )

    writer.commit(mergetype=writing.CLEAR)


def media_rebuild():
    print datetime.datetime.now()
    print 'media_rebuild'
    media_db = mysql_new.BaseDB(config.MYSQL_DEFINE_MEDIA)
    schema = Schema(movieid = ID(stored=True, unique=True),
                title=TEXT(stored=True, analyzer=analyzer_zhongwen, field_boost=2.0),
                pinyin_title = TEXT(stored=True, analyzer=analyzer_pinyin, field_boost=2.0),
                director=KEYWORD(stored=True),
                year=NUMERIC(stored=True, sortable=True),
                score=NUMERIC(stored=True, sortable=True),
                area=KEYWORD(stored=True),
                description=TEXT(stored=True, field_boost=1.5),
                pinyin_description = TEXT(stored=True, field_boost=1.0),
                actor=KEYWORD(stored=True, field_boost=1.0),
                pinyin_actor=TEXT(stored=True, field_boost=1.0),
                genres=KEYWORD(stored=True, field_boost=1.0),
                pinyin_genres = TEXT(stored=True, field_boost=1.0),
                type=NUMERIC(stored=True),
                source=NUMERIC(stored=True)
                )
    SQL = '''SELECT `movieid`, `title`, `type`, `actor`, `genres`, `director`, `douban_score`, `introduction` as description, `year` FROM `media_info` WHERE `status`=1 AND type in ('movie', 'tv', 'teleplay', 'anime')
          '''
    res = media_db.query(SQL, ())
    if not res:
        return
    for info in res:
        if info.get('type') == 'movie':
            info['type'] = 1
        elif info.get('type') == 'teleplay':
            info['type'] = 2
        elif info.get('type') == 'tv':
            info['type'] = 3;
        elif info.get('type') == 'anime':
            info['type'] = 4
        else:
            continue
    index_path = os.path.join(config.index_root_dir, 'media')
    if not os.path.exists(index_path):
        os.mkdir(index_path)
    #ix = create_in(index_path, schema=schema)
    storage = FileStorage(index_path)
    ix = storage.open_index()
    writer = ix.writer()
    for info in res:
        pinyin_title = ' '.join(lazy_pinyin(info.get('title').decode('utf8')))
        pinyin_description = ' '.join(lazy_pinyin(info.get('description').decode('utf8')))
        pinyin_actor = ''.join(info.get('actor', '').strip().split('/'))
        pinyin_actor = ' '.join(lazy_pinyin(pinyin_actor.decode('utf8')))
        pinyin_genres = ''.join(info.get('genres', '').strip().split('/'))
        pinyin_genres = ' '.join(lazy_pinyin(pinyin_genres.decode('utf8')))
        actor = ';'.join(info.get('actor', '').strip().split('/'))
        area = ';'.join(info.get('area', '').strip().split('/'))
        director = ';'.join(info.get('area', '').strip().split('/'))
        genres = ';'.join(info.get('genres','').strip().split('/'))

        writer.add_document(movieid = info.get('movieid').decode('utf8'),
                            title = info.get('title').decode('utf8'),
                            pinyin_title = pinyin_title,
                            type = info.get('type'),
                            actor = actor.decode('utf8'),
                            pinyin_actor = pinyin_actor,
                            genres = genres.decode('utf8'),
                            pinyin_genres = pinyin_genres,
                            director = director.decode('utf8'),
                            score = info.get('douban_score'),
                            description = info.get('description').decode('utf8'),
                            pinyin_description = pinyin_description,
                            area = area.decode('utf8'),
                            year = info.get('year')
                            )
    writer.commit(mergetype=writing.CLEAR)

def video_rebuild():
    print datetime.datetime.now()
    print 'video_rebuild'
    video_db = mysql_new.BaseDB(config.MYSQL_DEFINE_VIDEO)
    schema = Schema(movieid = ID(stored=True, unique=True),
                gcid = ID(stored=True),
                title=TEXT(stored=True, analyzer=analyzer_zhongwen),
                pinyin_title = TEXT(stored=True, analyzer=analyzer_pinyin),
                pic=ID(stored=True),
                cover_width=STORED,
                cover_height=STORED,
                uid=ID(stored=True),
                upline_time=DATETIME(stored=True, sortable=True),
                duration=STORED
                )

    SQL = '''SELECT video_id as `movieid`,`duration`,`upline_time`, `title`, `uid`, `pic`,`gcid`, `poster_width` as cover_width, `poster_height` as cover_height FROM `short_media_info_v2` WHERE `status` in (1,2)
          '''
    res = video_db.query(SQL, ())
    if not res:
        return
    index_path = os.path.join(config.index_root_dir, 'video')
    if not os.path.exists(index_path):
        os.mkdir(index_path)
    ix = create_in(index_path, schema=schema)
    storage = FileStorage(index_path)
    ix = storage.open_index()
    writer = ix.writer()
    for info in res:
        pinyin_title = ' '.join(lazy_pinyin(info.get('title').decode('utf8')))
        writer.add_document(movieid = str(info.get('movieid')).decode('utf8'),
                            gcid = str(info.get('gcid')).decode('utf8'),
                            title = info.get('title').decode('utf8'),
                            pinyin_title = pinyin_title,
                            uid = str(info.get('uid')).decode('utf8'),
                            pic = info.get('pic').decode('utf8'),
                            cover_width = info.get('cover_width'),
                            cover_height = info.get('cover_height'),
                            duration=info.get('duration'),
                            upline_time=info.get('upline_time')
                            )
    writer.commit(mergetype=writing.CLEAR)


if __name__ == '__main__':
    # scheduler = BlockingScheduler()
    # scheduler.add_job(pub_rebuild, 'cron', minute='*/30')
    # scheduler.add_job(media_rebuild, 'cron', hour='4')
    # scheduler.add_job(video_rebuild, 'cron', hour='*/3')
    # scheduler.start()
    #pub_rebuild()
    #media_rebuild()
    video_rebuild()



