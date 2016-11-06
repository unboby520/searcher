# coding:utf8
"""

Models
----

Data Access Layer.

Author: ilcwd
"""
from slutils import mysql, misc, mysql_new
from searcher.core import config, constants
searcher_db = mysql_new.BaseDB(config.MYSQL_DEFINE)