# -*- coding: utf-8 -*-
import hashlib
import random
import time
import urllib

from slutils import mysql, misc, mysql_new
from qiniu import Auth
from searcher.core import config, constants
from . import searcher_db
from collections import defaultdict
from ..models import redis_model

def get_hot_event():
    SQL = '''SELECT `id`, `word` AS keyword, `type` FROM `hot_event` ORDER BY `id`
          '''
    res = searcher_db.query(SQL, ())
    if not res:
        return constants.CODE_OK, []
    return constants.CODE_OK, res


def get_hot_res():
    SQL = '''SELECT `res_id` as uid FROM `hot_res` WHERE `res_type`='pub' ORDER BY `id`
          '''
    res = searcher_db.query(SQL, ())
    if not res:
        return constants.CODE_OK, []
    return constants.CODE_OK, res


def add_hot_event(keyword, type):
    SQL = '''INSERT INTO hot_event(`word`, `type`) VALUES (%s, %s)
          '''
    res = searcher_db.execute(SQL, (str(keyword), str(type)))
    return constants.CODE_OK, 1


def drop_hot_event(id):
    SQL = '''DELETE FROM hot_event WHERE `id`=%s LIMIT 1
          '''
    res = searcher_db.execute(SQL, (int(id), ))
    return constants.CODE_OK, 1


def add_hot_pub(uid):
    SQL = '''INSERT INTO `hot_res`(`res_type`, `res_id`) VALUES ('pub', %s)
          '''
    res = searcher_db.execute(SQL, (str(uid),))
    return constants.CODE_OK, 1



def drop_hot_pub(uid):
    SQL = '''DELETE FROM hot_res WHERE `res_id`=%s LIMIT 1
          '''
    res = searcher_db.execute(SQL, (str(uid),))
    return constants.CODE_OK, 1