# -*- coding:utf-8 -*-
__all__ = ['log']

import logging
import logging.handlers

from ._config import SCRIPT_PATH

logging._srcfile = None
logging.logThreads = False
logging.logProcesses = False
logging.logMultiprocessing = False
logging.raiseExceptions = False
#logging.Formatter.default_msec_format = '%s.%03d'


class _Logger(logging.Logger):
    """
    自定义的日志记录类

    Args:
        name (str): 日志文件名(不含扩展名)
    """

    def __init__(self, name: str) -> None:
        super().__init__(name)

        log_dir = SCRIPT_PATH.parent / 'log'
        log_dir.mkdir(0o755, exist_ok=True)

        log_filepath = log_dir / f'{SCRIPT_PATH.stem}.log'
        file_handler = logging.handlers.TimedRotatingFileHandler(
            str(log_filepath), when='MIDNIGHT', backupCount=5, encoding='utf-8')

        import sys
        stream_handler = logging.StreamHandler(sys.stdout)

        file_handler.setLevel(logging.INFO)
        stream_handler.setLevel(logging.DEBUG)

        formatter = logging.Formatter(
            "<{asctime}> [{levelname}] {message}", datefmt='%Y-%m-%d %H:%M:%S', style='{')
        formatter.default_msec_format
        file_handler.setFormatter(formatter)
        stream_handler.setFormatter(formatter)

        self.addHandler(file_handler)
        self.addHandler(stream_handler)


log = _Logger(__name__)
