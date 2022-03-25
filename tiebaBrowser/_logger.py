# -*- coding:utf-8 -*-
__all__ = ['MyLogger', 'log']


import logging
import logging.handlers
import sys

from ._config import SCRIPT_PATH


class MyLogger(logging.Logger):
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
        try:
            file_handler = logging.handlers.TimedRotatingFileHandler(
                str(log_filepath), when='D', backupCount=5, encoding='utf-8')
        except Exception:
            try:
                log_filepath.unlink()
            except:
                raise OSError(f"Unable to read or remove {log_filepath}")
            else:
                file_handler = logging.handlers.TimedRotatingFileHandler(
                    str(log_filepath), when='D', backupCount=5, encoding='utf-8')

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
