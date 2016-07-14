#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
import logging.handlers
import os

app_path = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))


class LogConfig(object):
    def __init__(self, log_name='', file_name=app_path + '/log/inspect_data.log'):
        self.__logger = logging.getLogger(log_name)
        self.__logger.setLevel(logging.DEBUG)
        # fh = logging.FileHandler(file_name)
        # fh.setLevel(logging.INFO)
        fh = logging.handlers.RotatingFileHandler(file_name, maxBytes=1024*1024, backupCount=5)
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


loggerWrapper = LogConfig('web_py').InitLogger()

'''useing example (same as logging in python lib)
from log import loggerWrapper as logging
logging.info(....)
'''

if __name__ == '__main__':
    pass
