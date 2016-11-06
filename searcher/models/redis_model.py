
try:
    import ujson as json
except:
    import json
import rediscluster
import functools
from searcher.core import (config, constants)
import types
import flask


follow_cache = rediscluster.StrictRedisCluster(
    startup_nodes=config.REDIS_CLUSTER_PARAMS)


def set_cache(KEY, VALUE):
    follow_cache.set(str(KEY), VALUE)


def get_cache(KEY):
    value = follow_cache.get(str(KEY))
    return value


def set_h_cache(FILED, KEY, VALUE):
    follow_cache.hset(FILED, str(KEY), VALUE)


def get_h_cache(field, KEY):
    value = follow_cache.hget(field, str(KEY))
    return value

def get_hm_cache(field, KEY):
    value = follow_cache.hmget(field, KEY)
    return value

def cache_group_info(func):
    """cache db"""
    @functools.wraps(func)
    def wrapper(group_id, offset, size, field=constants.REDIS_FOLLOW_GROUP_INFO):
        res = get_h_cache(field, group_id)
        if not res:
            code, res = func(group_id, offset, size)
            if res:
                set_h_cache(field, group_id, json.dumps(res))
        else:
            res = json.loads(res)
        if not isinstance(res, types.DictType):
            return constants.CODE_DATA_ERROR, res

        return constants.CODE_OK, res

    return wrapper


def cache_group_res_count(func):
    @functools.wraps(func)
    def wrapper(group_id, field=constants.REDIS_GROUP_FOLLOW_COUNT):
        res = get_h_cache(field, group_id)
        if not res:
            code, res = func(group_id)
            if res:
                set_h_cache(field, group_id, res)
        return constants.CODE_OK, res
    return wrapper


def get_grouplist_res_count(group_list):
    result = follow_cache.hmget(constants.REDIS_GROUP_FOLLOW_COUNT,group_list)
    return {str(group_id):result[index] for index, group_id in enumerate(group_list)}


def clean_cache_group_res_count(group_id):
    result = follow_cache.hdel(constants.REDIS_GROUP_FOLLOW_COUNT, group_id)


if __name__ == '__main__':
    print clean_cache_group_res_count(2)
    print get_grouplist_res_count(['2', '3'])
