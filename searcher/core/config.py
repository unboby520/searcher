# coding: utf8
#
# searcher - config
# 
# Author: ilcwd 
# Create: 15/5/11
from .config_client import Client
import os

ENV_TEST = "TEST"
ENV_DEV = "DEV"
ENV_PRE = "PRE"
ENV_PRODUCT = "PRODUCT"

ENV = os.getenv("SL_ENV", ENV_TEST)

CFG_HOST = {
    'TEST':'10.10.28.2',
    'PRE' : '10.33.1.132',
    'PRODUCT':'10.33.1.132'
}.get(ENV)

CFG_PREFIX = {
    'TEST':'dev/service/searcher/',
    'PRE' : 'preview/service/searcher/',
    'PRODUCT':'production/service/searcher/'
}.get(ENV)

sentry_dsn = {
    'TEST':'http://e295412421024de9be2c97e460b879a5:ff1dfe3fa4c441c8864b8e094a2c1bc5@10.10.28.2:9000/6',
    'PRE':'http://2eb3177b46fd4801a8317b151659405d:f37d4ec8ad2d432782a4477cad1f86c3@tw06132.sandai.net:9000/47',
    'PRODUCT':'http://0c84c687e9ed41cb9800a7d00d951db3:41ff449e3888401daccf39ee9593910a@tw06132.sandai.net:9000/44'
}.get(ENV)

client = Client(CFG_HOST)

SL_INTER_HOST = client.get_str(CFG_PREFIX + 'SL_INTER_HOST')
URLSITTER_HOST = client.get_str(CFG_PREFIX + 'URLSITTER_HOST')
REDIS_CLUSTER_PARAMS = client.get_json(CFG_PREFIX + 'REDIS_CLUSTER_PARAMS')
MYSQL_DEFINE = client.get_json(CFG_PREFIX + 'MYSQL_DEFINE')

MYSQL_DEFINE_MEDIA = client.get_json(CFG_PREFIX + 'MYSQL_DEFINE_MEDIA')
MYSQL_DEFINE_PUB = client.get_json(CFG_PREFIX + 'MYSQL_DEFINE_PUB')
MYSQL_DEFINE_VIDEO = client.get_json(CFG_PREFIX + 'MYSQL_DEFINE_VIDEO')

index_root_dir = '/dev/shm/index'


