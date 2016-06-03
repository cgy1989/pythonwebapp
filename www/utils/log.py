#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging


class LogConfig(object):
    def __init__(self, logName='', fileName='../../log/web.log'):
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

    def InitLogger(self):
        return self.__logger

logger = LogConfig('web_py').InitLogger()


if __name__ == '__main__':
    pass

