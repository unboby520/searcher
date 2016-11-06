#-*- coding:utf8 -*-
import flask

from ..core import (success_response, error_response)
from ..core import (config, constants)
from ..models import mysql_model as _mysql
from ..models.remote_pp_info import get_pp_info
from ..models import formatURL
from ..models import search_model as _search
from ..models import remote_urlsitter
import urllib

app = flask.Blueprint('searcher', __name__)

@app.route('/hot_search', strict_slashes=False, methods=['GET'])
def hot_search():
    code, hot_event = _mysql.get_hot_event()
    code, hot_res = _mysql.get_hot_res()
    uid_list = [r.get('uid') for r in hot_res]
    uid_list = [uid for uid in uid_list if uid]
    code, uid_info = get_pp_info(uid_list)
    for info in hot_res:
        if not info:
            continue
        uid = info.get('uid')
        userinfo = uid_info.get(str(uid))
        if not userinfo:
            continue
        else:
            info['title'] = userinfo.get('title')
            info['kind'] = userinfo.get('kind')
            info['description'] = userinfo.get('description')
            info['v_status'] = userinfo.get('v_status')
            info['fans_count'] = userinfo.get('fans_count')
            if str(userinfo.get('kind')) == 'pub' and not str(userinfo.get('icon_url')).startswith('http'):
                userinfo['icon_url'] =  formatURL.formatPoster(userinfo.get('icon_url'))
            else:
                info['icon_url'] = userinfo.get('icon_url')
    return success_response({"result": "ok", "hot_event":hot_event, "pub":hot_res})


@app.route('/all_search', strict_slashes=False, methods=['GET'])
def all_search():
    args = flask.request.args
    keyword = args.get('keyword', None)
    media_size = args.get('media_size', 4) or 4
    pub_size = args.get('pub_size', 4) or 4
    video_size = args.get('video_size', 4) or 4
    if not keyword:
        return error_response({'result':constants.CODE_BAD_PARAMS})
    if int(media_size):
        code, res_media, count_media = _search.search_media(keyword, 1, media_size)
    else:
        res_media = []
        count_media = 0
    if int(video_size):
        code, res_video, count_video = _search.search_video(keyword, 1, video_size)
    else:
        res_video = []
        count_video = 0
    if int(pub_size):
        code, res_pub, count_pub = _search.search_pub(keyword, 1, pub_size)
    else:
        count_pub = 0
        res_pub = []

    for info in res_media:
        info.pop('pinyin_title')
        info['actor'] = [] if not info.get('actor') else info.get('actor').split(';')
        info['director'] = [] if not info.get('director') else info.get('director').split(';')
        info['area'] = [] if not info.get('area') else info.get('area').split(';')
        info['genres'] = [] if not info.get('genres') else info.get('genres').split(';')
        info['cover_url'] = formatURL.gen_poster_url(info.get('movieid'), 't', 160, 226)
        info['source'] = 1

    video_gcid_list = [video.get('gcid') for video in res_video]
    url_info_list = remote_urlsitter.geturl_v2(video_gcid_list)
    for index, info in enumerate(res_video):
        url_info = url_info_list[index]
        info['cover_url'] = url_info.get('cover_url')
        info['play_url'] = url_info.get('play_url')
    uid_list = [str(video.get('uid')) for video in res_video]
    code, user_info = get_pp_info(uid_list)
    user_info = {} if not user_info else user_info
    for video in res_video:
        uid = video.get('uid')
        user = user_info.get(str(uid))
        video['user_info'] =  user
    for info in res_pub:
        info.pop('pinyin_title')

    result = {
            "result": constants.CODE_OK,
            "media": {
                "count": count_media,
                "list": res_media
            },
            "pub": {
                "count": count_pub,
                "list": res_pub
            },
            "video": {
                "count": count_video,
                "list": res_video
            }
        }
    return success_response(result)


@app.route('/res_search', strict_slashes=False, methods=['GET'])
def res_search():
    args = flask.request.args
    keyword = args.get('keyword', None)
    page = args.get('page', 1)
    pagelen = args.get('pagelen', 8)
    res_type = args.get('type', 'video')

    if res_type != 'video' or not keyword:
        return error_response({'result':constants.CODE_BAD_PARAMS})
    code, res_video, count_video = _search.search_video(keyword, page, pagelen)
    video_gcid_list = [video.get('gcid') for video in res_video]
    url_info_list = remote_urlsitter.geturl_v2(video_gcid_list)
    for index, info in enumerate(res_video):
        url_info = url_info_list[index]
        info['cover_url'] = url_info.get('cover_url')
        info['play_url'] = url_info.get('play_url')
    uid_list = [str(video.get('uid')) for video in res_video]
    code, user_info = get_pp_info(uid_list)
    user_info = {} if not user_info else user_info
    for video in res_video:
        uid = video.get('uid')
        user = user_info.get(str(uid))
        video['user_info'] =  user

    data = {
        "result": "ok",
        "count":count_video,
        "video": res_video
    }
    return success_response(data)