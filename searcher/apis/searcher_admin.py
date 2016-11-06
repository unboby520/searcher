#-*- coding:utf8 -*-
import flask

from ..core import (success_response, error_response)
from ..core import (config, constants)
from ..models import mysql_model as _mysql
from ..models.remote_pp_info import get_pp_info
from ..models import formatURL
from ..models import search_model as _search
import urllib

app = flask.Blueprint('searcher_admin', __name__)

@app.route('/hot_event_list', strict_slashes=False, methods=['GET'])
def hot_event_list():
    code, res = _mysql.get_hot_event()
    return success_response({"result": "ok", "list":res})

@app.route('/hot_pub_list', strict_slashes=False, methods=['GET'])
def hot_pub_list():
    code, pub_list = _mysql.get_hot_res()
    uid_list = [info.get('uid') for info in pub_list]
    code, user_info = get_pp_info(uid_list)
    res_list = []
    for uid in uid_list:
        user = user_info.get(str(uid))
        if not user:
            continue
        info = {}
        info['title'] = user.get('title')
        info['uid'] = user.get('uid')
        info['kind'] = user.get('kind')
        info['icon_url'] = user.get('icon_url')
        info['update_time'] = user.get('update_time')
        res_list.append(info)
    return success_response({"result": "ok", "list":res_list})

@app.route('/add_hot_event', strict_slashes=False, methods=['POST'])
def add_hot_event():
    args = flask.request.json
    keyword = args.get('keyword', None)
    event_type = args.get('type', 'video')
    _mysql.add_hot_event(keyword, event_type)
    return success_response({"result":"ok"})

@app.route('/drop_hot_event', strict_slashes=False, methods=['POST'])
def drop_hot_event():
    args = flask.request.json
    event_id = args.get('id', None)
    _mysql.drop_hot_event(event_id)
    return success_response({"result":"ok"})


@app.route('/add_hot_pub', strict_slashes=False, methods=['POST'])
def add_hot_pub():
    args = flask.request.json
    uid = args.get('uid', None)
    _mysql.add_hot_pub(uid)
    if not uid:
        return error_response({'result':constants.CODE_BAD_PARAMS})
    return success_response({"result":"ok"})

@app.route('/drop_hot_pub', strict_slashes=False, methods=['POST'])
def drop_hot_pub():
    args = flask.request.json
    uid = args.get('uid', None)
    _mysql.drop_hot_pub(uid)
    if not uid:
        return error_response({'result':constants.CODE_BAD_PARAMS})
    return success_response({"result":"ok"})