# coding:utf8
"""
A wrapper for module `_mysql`,
more efficient than mysqldb.

Author: ilcwd
"""

from threading import local
import functools
import logging
import datetime
import time

import _mysql
from _mysql_exceptions import (
    IntegrityError,
    OperationalError,
)

__all__ = [
    'QUERY_TUPLE',
    'QUERY_DICT',
    'SQLOperationalError',
    'is_lost_connection_exception',
    'BaseDB'
    'escape',
]

QUERY_TUPLE = 0
QUERY_DICT = 1
DEFAULT_CHARSET = 'utf8'

SQL_KEY_ERROR = -2

SQLOperationalError = OperationalError
_logger = logging.getLogger(__name__)


class DBError(Exception):
    pass


def escape(sql):
    """
    :param sql:
    :return: a type<str> object,
    """
    if sql is None:
        return ''

    if isinstance(sql, unicode):
        sql = sql.encode('utf8')

    if isinstance(sql, (int, long, float)):
        return str(sql)

    if isinstance(sql, datetime.datetime):
        return sql.strftime("%Y-%m-%d %H:%M:%S")

    if not isinstance(sql, str):
        raise DBError("Invalid value: %s, unexpected type %s" % (str(sql), type(sql)))

    safe_sql = _mysql.escape_string(sql)
    return safe_sql


class DBConnection(object):
    CONNECTION_IDLE_TIMEOUT = 600

    def __init__(self, **kw):
        self._db_params = kw.copy()
        self._charset = self._db_params.pop('charset')
        # 分表代表CLIENT_MULTI_RESULTS 和 CLIENT_MULTI_STATEMENTS
        self._db_params['client_flag'] = 131072 | 65536

        self._mysql = None
        self._last_used = 0
        self.is_closed = False
        self.inside_transaction = False
        self.is_occupied = False
        self.reconnect()

    @classmethod
    def set_global_idle_timeout(cls, timeout):
        cls.CONNECTION_IDLE_TIMEOUT = int(timeout)

    def set_inside_transaction(self, b):
        self.inside_transaction = bool(b)

    def reconnect(self):
        self.close()

        conn = _mysql.connect(**self._db_params)
        conn.set_character_set(self._charset)
        conn.autocommit(True)
        self._mysql = conn

        self._last_used = time.time()
        self.inside_transaction = False
        self.is_closed = False

    def _is_timeout(self):
        return abs(self._last_used - time.time()) > self.CONNECTION_IDLE_TIMEOUT

    def close(self):
        if self._mysql is not None:
            self._mysql.close()
            self.is_closed = True
            self._mysql = None
            self._last_used = 0

    def __str__(self):
        formatter = "mysql://%(user)s@%(host)s:%(port)d/%(db)s"
        return formatter % self._db_params

    def get_connection(self):
        if self.is_closed:
            raise DBError("DB object is closed")

        if self._is_timeout():
            _logger.info("Connection timeout reached(%s), reconnect: %s",
                         self._last_used, str(self))
            self.reconnect()
        return self._mysql


def set_db_connection_idle_timeout(timeout):
    DBConnection.set_global_idle_timeout(timeout)


def is_lost_connection_exception(ex):
    if isinstance(ex, OperationalError):
        if ex.args and isinstance(ex.args, (list, tuple)):
            if ex.args[0] in (
                    2003,  #Can't connect to MySQL server
                    2006,  # MySQL server has gone away
                    2013,  # Lost connection to MySQL server during query
                    1213,
                    1205,  # Lock wait timeout exceeded; try restarting transaction
            ):
                return True
    return False


def db_executor_retry(func):
    """retry once when lost connection error raise."""

    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        try:
            result = func(self, *args, **kwargs)
        except OperationalError as e:
            if not is_lost_connection_exception(e):
                raise

            self.reconnect()

            conn = self._get_connection()
            _logger.info("DB retry error, db is %s, error is %s", conn, e)
            result = func(self, *args, **kwargs)
        return result

    return wrapper


class QueryWrapper(object):
    """
    Query Wrapper for _mysql.connection.

    Attentions:
        * not thread safe, don't share with other threads
    """
    def __init__(self, conn):
        if conn.is_occupied:
            raise DBError("Connection is occupied by others,")

        self.conn = conn

    def __enter__(self):
        self.query("BEGIN")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.query("ROLLBACK")
        else:
            self.query("COMMIT")

    def execute(self, sql):
        conn = self.conn.get_connection()
        try:
            conn.query(sql)
            rows = conn.affected_rows()
            # 这个值与驱动、系统、硬件CPU位数都可能有关
            if rows == 0xFFFFFFFFFFFFFFFF:  # 64位的-1
                rows = 0

            # assert conn.next_result() == -1, sql
            return rows
        except IntegrityError:
            return SQL_KEY_ERROR

    def query(self, sql, how=QUERY_TUPLE):
        conn = self.conn.get_connection()
        conn.query(sql)
        res = conn.store_result()
        if res:
            result = res.fetch_row(res.num_rows(), how)
            assert conn.next_result() == -1, sql
            return result
        else:
            return ()

    def query_one(self, sql, how=QUERY_TUPLE):
        rows = self.query(sql, how)
        if rows:
            return rows[0]
        return None

    def insert(self, sql):
        conn = self.conn.get_connection()
        try:
            conn.query(sql)
            rows = conn.affected_rows()
            # 这个值与驱动、系统、硬件CPU位数都可能有关
            if rows == 0xFFFFFFFFFFFFFFFF:  # 64位的-1
                rows = 0
            insertid = conn.insert_id()

            # assert conn.next_result() == -1, sql
            return insertid, rows
        except IntegrityError:
            return -1, SQL_KEY_ERROR

    def call_procedure(self, procedure, params=None, how=QUERY_TUPLE):
        conn = self.conn.get_connection()

        def _obj_to_str(obj):
            if isinstance(obj, (int, long)):
                return str(obj)
            else:
                return '"%s"' % escape(obj)

        if isinstance(params, (list, tuple)):
            sargs = ','.join(map(_obj_to_str, params))
            conn.query('CALL %s(%s)' % (procedure, sargs))
        elif params is None:
            conn.query('CALL %s()' % (procedure, ))
        else:
            conn.query('CALL %s("%s")' % (procedure, escape(params)))

        ret = []
        res = conn.store_result()
        if res:
            ret.append(res.fetch_row(res.num_rows(), how))
            # 0 - success
            # -1 - success and no more results
            # >0 - error
            while conn.next_result() != -1:
                res = conn.store_result()
                if res:
                    ret.append(res.fetch_row(res.num_rows(), how))

        return ret


class BaseDB(local):
    def __init__(self, dbconfig):
        self.config = dbconfig.copy()
        if not 'charset' in self.config:
            self.config['charset'] = DEFAULT_CHARSET
        self.conn = DBConnection(**self.config)

    def _get_connection(self):
        return self.conn

    def reconnect(self):
        self.conn.reconnect()

    def close(self):
        self.conn.close()

    @db_executor_retry
    def execute(self, sql):
        return QueryWrapper(self._get_connection()).execute(sql)

    @db_executor_retry
    def query(self, sql, how=QUERY_TUPLE):
        return QueryWrapper(self._get_connection()).query(sql, how)

    @db_executor_retry
    def query_one(self, sql, how=QUERY_TUPLE):
        return QueryWrapper(self._get_connection()).query_one(sql, how)

    @db_executor_retry
    def insert(self, sql):
        """
        :param sql:
        :return: insert_id, affected_rows
        """
        return QueryWrapper(self._get_connection()).insert(sql)

    @db_executor_retry
    def call_procedure(self, procedure, params=None, how=QUERY_TUPLE):
        """调用存储过程
        Attentions:
            * param `procedure` is not safe
        """
        return QueryWrapper(self._get_connection()).call_procedure(procedure, params, how)

    def session(self):
        """
        Create a transaction.

        Examples:

            mydb = BaseDB(myconfig)
            # *do not* share `conn` outside!!
            with mydb.session() as conn:
                conn.query("SHOW TABLES")

        Attentions:

            * donot deal with `OperationalError`, try and catch it yourself.

        """
        return QueryWrapper(self._get_connection())
