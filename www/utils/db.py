#!/usr/bin/python
# -*- coding: utf-8 -*-

from log import logger as log
import time
import uuid
import threading
import functools
import pymysql


class Dict(dict):
    def __init__(self, names=(), values=(), **kwargs):
        super(Dict, self).__init__(**kwargs)
        for k, v in zip(names, values):
            self[k] = v;

    '''
    def __getattribute__(self, key):
        print '__getattribute__ call'
        return dict.__getattribute__(self, key)
    '''

    def __getattr__(self, key):
        # print '__getattr__ call'
        try:
            return self[key]
        except KeyError:
            raise AttributeError(r"'Dict' object has no attribute 's' " % key)

    def __setattr__(self, key, value):
        self[key] = value


def next_id(t=None):
    if t is None:
        t = time.time()
        return '%015d%s000' % (int(t * 1000), uuid.uuid4().hex)


def profiling(start, sql=''):
    t = time.time() - start
    if t > 0.1:
        log.warning('[PROFILING] [DB] %s: %s', t, sql)
    else:
        log.info('[PROFILING] [DB] %s: %s', t, sql)


def DBError(Exception):
    pass


def MultiConlumnsError(DBError):
    pass


class _LasyConnection(object):
    def __init__(self):
        self.connection = None

    def cursor(self):
        global engine
        if self.connection is None:
            con = engine.connect()
            log.info('open connection <%s>...' % hex(id(connection)))
            self.connection = con
        return self.connection.cursor()

    def commit(self):
        self.connection.commit()

    def rollback(self):
        self.connection.rollback()

    def cleanup(self):
        if self.connection:
            con = self.connection
            self.connection = None
            log.info('close connection <%s>...' % hex(id(con)))
            con.close()


class _DbCtx(threading.local):
    """
    Thread local object that holds connection info.
    """
    def __init__(self):
        self.connection = None
        self.transactions = 0

    def is_init(self):
        return not self.connection is None

    def init(self):
        log.info('open lazy connection...')
        self.connection = _LasyConnection()
        self.transactions = 0

    def cleanup(self):
        self.connection.cleanup()
        self.connection = None

    def cursor(self):
        return self.connection.cursor()


_db_ctx = _DbCtx()

engine = None


class _Engine(object):

    def __init__(self, connect):
        self._connect = connect

    def connect(self):
        return self._connect()


def create_engine(user, password, database, host='127.0.0.1', port=3306, **kwargs):
    global engine
    if engine is not None:
        log.warning('Engine is already initialized.')
        return False
    params = dict(user=user, password=password, database=database, host=host, port=port)
    defaults = dict(use_unicode=True, charset='utf8', autocommit=False)
    for k, v in defaults.iteritems():
        params[k] = kwargs.pop(k, v)
    params.update(kwargs)
    engine = _Engine(lambda: pymysql.connect(**params))
    return True


class _ConnectionCtx(object):
    def __enter__(self):
        global _db_ctx
        self.should_cleanup = False
        if not _db_ctx.is_init():
            _db_ctx.init()
            self.should_cleanup = True
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        global _db_ctx
        if self.should_cleanup:
            _db_ctx.cleanup()


def connection():
    return _ConnectionCtx()


def with_connection(func):
    @functools.wraps(func)
    def _wrapper(*args, **kw):
        with _ConnectionCtx():
            return func(*args, **kw)
    return _wrapper

'''
# decorated function example
def my_decorator(func):
    @functools.wraps(func)
    def wrapper(*args, **kw):
        log.info('calling decorated function')
        return func(*args, **kw)
    return wrapper


@my_decorator
def example():
    log.info('call example function')

example()
'''


class _TransactionCtx(object):

    def __enter__(self):
        global _db_ctx
        self.should_close_conn = False
        if not _db_ctx.is_init():
            # needs open a connection first:
            _db_ctx.init()
            self.should_close_conn = True
        _db_ctx.transactions += 1
        log.info('begin transaction...' if _db_ctx.transactions == 1 else 'join current transaction...')
        return self

    def __exit__(self, exctype, excvalue, traceback):
        global _db_ctx
        _db_ctx.transactions -= 1
        try:
            if _db_ctx.transactions == 0:
                if exctype is None:
                    self.commit()
                else:
                    self.rollback()
        finally:
            if self.should_close_conn:
                _db_ctx.cleanup()

    def commit(self):
        global _db_ctx
        log.info('commit transaction...')
        try:
            _db_ctx.connection.commit()
            log.info('commit ok.')
        except:
            log.warning('commit failed. try rollback...')
            _db_ctx.connection.rollback()
            log.warning('rollback ok.')
            raise

    def rollback(self):
        global _db_ctx
        log.warning('rollback transaction...')
        _db_ctx.connection.rollback()
        log.info('rollback ok.')


def transaction():
    return _TransactionCtx()


def with_transaction(func):
    @functools.wraps(func)
    def _wrapper(*args, **kwargs):
        with _TransactionCtx():
            return func(*args, **kwargs)
    return _wrapper


def _select(sql, first, *args):
    global _db_ctx
    cursor = None
    sql = sql.replace('?', '%s')
    log.info('SQL: %s, ARGS: %s', sql, args)
    try:
        cursor = _db_ctx.connection.cursor()
        cursor.execute(sql, args)
        if cursor.description:
            names = [x[0] for x in cursor.description]
        if first:
            values = cursor.fetchone()
            if not values:
                return None
            return Dict(names, values)
        return [Dict(names, x) for x in cursor.fetchall()]
    finally:
        if cursor:
            cursor.close()


@with_connection
def select_one(sql, *args):
    return _select(sql, True, *args)


@with_connection
def select(sql, *args):
    return _select(sql, False, *args)


@with_connection
def _update(sql, *args):
    global _db_ctx
    cursor = None
    sql = sql.replace('?', '%s')
    log.info('SQL: %s, ARGS: %s' % (sql, args))
    try:
        cursor = _db_ctx.connection.cursor()
        cursor.execute(sql, args)
        r = cursor.rowcount
        if _db_ctx.transactions == 0:
            # no transaction enviroment:
            log.info('auto commit')
            _db_ctx.connection.commit()
        return r
    finally:
        if cursor:
            cursor.close()


def insert(table, **kwargs):
    cols, args = zip(*kwargs.iteritems())
    #cols = kwargs.keys()
    #args = kwargs.values()
    sql = 'insert into `%s` (%s) values (%s)' % \
          (table, ','.join(['`%s`' % col for col in cols]), ','.join(['?' for i in range(len(cols))]))
    return _update(sql, *args)


def update(sql, *args):
    return _update(sql, *args)

'''
test transaction code
@with_transaction
def some_work():
    u = dict(name='chen', email='chen@test.org', passwd='chen', last_modified=time.time())
    insert('user', **u)
    update('update user set name="suhong" where id = 105')
'''

if __name__ == '__main__':
    create_engine('root', 'root', 'mytestdb')
    u = dict(name='chen', email='chen@test.org', passwd='chen', last_modified=time.time())
    insert('user', **u)


