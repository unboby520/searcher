#-*- coding:utf8 -*-
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
from whoosh.qparser import MultifieldParser
import sys
sys.path.append('/data/apps/searcher/current')
from searcher.models import config

def test_pub():
    index_path = os.path.join(config.index_root_dir, 'pub')
    storage = FileStorage(index_path)
    ix = storage.open_index()
    with ix.searcher() as searcher:
        print list(searcher.lexicon('title'))
        myquery = Term('title', u'电影')
        results = searcher.search(myquery)
        # tc = searcher.collector(limit=5)
        # tlc = TimeLimitCollector(tc, timelimit=1)   #limit seacher time
        # searcher.search_with_collector(myquery, tlc)
        for hit in results:
            print hit.fields()

def test_media():
    index_path = os.path.join(config.index_root_dir, 'media')
    storage = FileStorage(index_path)
    ix = storage.open_index()
    with ix.searcher() as searcher:
        #print list(searcher.lexicon('title'))
        myquery = Term('title', u'尾巴')
        #myquery = Term('movieid', u'mi1022160')

        tc = searcher.collector(limit=200)
        tlc = TimeLimitCollector(tc, timelimit=1)   #limit seacher time
        searcher.search_with_collector(myquery, tlc)
        for hit in tlc.results():
            #print hit.fields()
            print hit.fields()


def test_video():
    index_path = os.path.join(config.index_root_dir, 'video')
    storage = FileStorage(index_path)
    ix = storage.open_index()
    with ix.searcher() as searcher:
        #print list(searcher.lexicon('title'))
        myquery = Term('title', u'全面')
        #myquery = Term('movieid', u'mi1022160')
        tc = searcher.collector(limit=20)
        tlc = TimeLimitCollector(tc, timelimit=1)   #limit seacher time
        searcher.search_with_collector(myquery, tlc)
        #for hit in tlc.results():
            #print hit.fields()
        #    print hit.fields().get('title')
        print '==========================='
        results = searcher.search_page(myquery, 1, 10)
        #for hit in results:
        #    print hit.fields().get('title')
        print '==============================='
        parser = MultifieldParser(['title', 'pinyin_title'], ix.schema)
#    parser = QueryParser('title', schema = ix.schema)
        q = parser.parse(u'quan mian')
        results = searcher.search_page(q, 1, 10)
        for hit in results:
            print hit.fields()


if __name__ == '__main__':
    test_video()
