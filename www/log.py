#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging


class LoggerWrapper(object):
    def __init__(self, logName='', fileName='../log/web.log'):
        self.__logger = logging.getLogger(logName)
        self.__logger.setLevel(logging.DEBUG)
        fh = logging.FileHandler(fileName)
        fh.setLevel(logging.INFO)
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(filename)s:%(lineno)d %(asctime)s %(levelname)s::%(message)s')
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        self.__logger.addHandler(fh)
        self.__logger.addHandler(ch)

    def log_debug(self, formatter, *args):
        self.__logger.debug(formatter % args)

    def log_info(self, formatter, *args):
        self.__logger.info(formatter % args)

    def log_warning(self, formatter, *args):
        self.__logger.warning(formatter % args)

    def log_error(self, formatter, *args):
        self.__logger.error(formatter % args)

__WebLog = LoggerWrapper('web_py', '../log/spam.log')


def debug(formatter, *args):
        __WebLog.log_debug(formatter % args)


def info(formatter, *args):
        __WebLog.log_info(formatter % args)


def warning(formatter, *args):
        __WebLog.log_warning(formatter % args)


def error(formatter, *args):
        __WebLog.log_error(formatter % args)


if __name__ == '__main__':
    debug('test1')
    info('test2')
    error('hahha %d', 10)
