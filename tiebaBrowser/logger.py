# -*- coding:utf-8 -*-
__all__ = ('SCRIPT_DIR',
           'MyLogger', 'log')


import os
import sys
from pathlib import Path
import time

import logging


SCRIPT_DIR = Path(sys.path[0])


class MyLogger(logging.Logger):
    """
    MyLogger(name=__name__)

    自定义的日志记录类
    """

    def __init__(self, name):

        super().__init__(name)

        log_dir = SCRIPT_DIR.joinpath('log')
        log_dir.mkdir(0o755, exist_ok=True)
        recent_time = time.strftime('%Y-%m-%d', time.localtime(time.time()))

        log_filepath = log_dir.joinpath(
            f'{SCRIPT_DIR.stem}_{recent_time}.log')
        try:
            file_handler = logging.FileHandler(
                str(log_filepath), encoding='utf-8')
        except:
            try:
                log_filepath.unlink()
            except:
                raise OSError(f"Unable to read or remove {log_filepath}")
            else:
                file_handler = logging.FileHandler(
                    str(log_filepath), encoding='utf-8')

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
