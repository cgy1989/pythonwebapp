#!/usr/bin/python
# -*- coding: utf-8 -*-

import uuid,time, logging


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
        #print '__getattr__ call'
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
        logging.warning('[PROFILING] [DB] %s: %s' % (t, sql))
    else:
        logging.info('[PROFILING] [DB] %s: %s' % (t, sql))


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%Y-%m-%d %I:%M:%S')
    start = time.time() - 10
    profiling(start)