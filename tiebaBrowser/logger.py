# -*- coding:utf-8 -*-
__all__ = ('SCRIPT_PATH', 'FILENAME', 'SHOTNAME',
           'MyLogger', 'log')


import os
import sys
import time

import logging


SCRIPT_PATH, FILENAME = os.path.split(os.path.realpath(sys.argv[0]))
SHOTNAME = os.path.splitext(FILENAME)[0]


class MyLogger(logging.Logger):
    """
    MyLogger(name=__name__)

    自定义的日志记录类
    """

    def __init__(self, name=__name__):

        super().__init__(__name__)

        log_dir = os.path.join(SCRIPT_PATH, 'log')
        if not os.path.exists(log_dir):
            os.mkdir(log_dir)
        recent_time = time.strftime('%Y-%m-%d', time.localtime(time.time()))

        log_filepath = os.path.join(log_dir, f'{SHOTNAME}_{recent_time}.log')
        try:
            file_handler = logging.FileHandler(log_filepath, encoding='utf-8')
        except:
            try:
                os.remove(log_filepath)
            except:
                raise OSError(f"Unable to read or remove {log_filepath}")
            else:
                file_handler = logging.FileHandler(
                    log_filepath, encoding='utf-8')

        stream_handler = logging.StreamHandler(sys.stdout)

        file_handler.setLevel(logging.INFO)
        stream_handler.setLevel(logging.DEBUG)

        formatter = logging.Formatter(
            "<%(asctime)s> [%(levelname)s] %(message)s", "%Y-%m-%d %H:%M:%S")
        file_handler.setFormatter(formatter)
        stream_handler.setFormatter(formatter)

        self.addHandler(file_handler)
        self.addHandler(stream_handler)
        self.setLevel(logging.DEBUG)


log = MyLogger(__name__)
