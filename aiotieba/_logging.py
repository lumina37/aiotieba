"""
日志记录

提供与标准库logging签名一致的六个函数debug/info/warning/error/critical/log
允许使用set_logger更换日志记录器
"""

import logging
import logging.handlers
import sys

logging.addLevelName(logging.FATAL, "FATAL")
logging.addLevelName(logging.WARN, "WARN")

logging.logThreads = False
logging.logProcesses = False
logging.logMultiprocessing = False
logging.raiseExceptions = False
logging.Formatter.default_msec_format = '%s.%03d'


class TiebaLogger(logging.Logger):
    """
    日志记录器

    Args:
        name (str): 日志文件名(不含扩展名)
    """

    file_log_level = logging.INFO
    stream_log_level = logging.DEBUG
    enable_file_log = True

    formatter = logging.Formatter("<{asctime}> [{levelname}] [{funcName}] {message}", style='{')

    __slots__ = [
        '_file_hd',
        '_stream_hd',
    ]

    def __init__(self, name: str) -> None:
        super().__init__(name)

        self._file_hd = None
        self._stream_hd = None

        if self.enable_file_log:
            self.addHandler(self.file_hd)
        self.addHandler(self.stream_hd)

    @property
    def file_hd(self) -> logging.handlers.TimedRotatingFileHandler:
        """
        指向log/xxx.log文件的日志handler
        """

        if self._file_hd is None:
            self._file_hd = logging.handlers.TimedRotatingFileHandler(
                f"log/{self.name}.log", when='MIDNIGHT', backupCount=5, encoding='utf-8'
            )
            self._file_hd.setLevel(self.file_log_level)
            self._file_hd.setFormatter(self.formatter)

        return self._file_hd

    @property
    def stream_hd(self) -> logging.StreamHandler:
        """
        指向标准输出流的日志handler
        """

        if self._stream_hd is None:
            self._stream_hd = logging.StreamHandler(sys.stdout)
            self._stream_hd.setLevel(self.stream_log_level)
            self._stream_hd.setFormatter(self.formatter)

        return self._stream_hd

_logger = None


def get_logger() -> TiebaLogger:
    global _logger

    if _logger is None:
        from pathlib import Path

        Path("log").mkdir(0o755, exist_ok=True)
        script_name = Path(sys.argv[0]).stem
        _logger = TiebaLogger(script_name)

    return _logger


def set_logger(logger: logging.Logger) -> None:
    """
    更换aiotieba的日志记录器

    Args:
        logger (logging.Logger)
    """

    global _logger
    _logger = logger


def set_formatter(formatter: logging.Formatter) -> None:
    """
    更换aiotieba的日志格式

    Args:
        formatter (logging.Formatter)
    """

    logger = get_logger()
    for hd in logger.handlers:
        hd.setFormatter(formatter)


def debug(msg, *args, **kwargs):
    """
    Log 'msg % args' with severity 'DEBUG'.

    To pass exception information, use the keyword argument exc_info with
    a true value, e.g.

    logger.debug("Houston, we have a %s", "thorny problem", exc_info=1)
    """

    logger = get_logger()
    logger.debug(msg, *args, **kwargs)


def info(msg, *args, **kwargs):
    """
    Log 'msg % args' with severity 'INFO'.

    To pass exception information, use the keyword argument exc_info with
    a true value, e.g.

    logger.info("Houston, we have a %s", "interesting problem", exc_info=1)
    """

    logger = get_logger()
    logger.info(msg, *args, **kwargs)


def warning(msg, *args, **kwargs):
    """
    Log 'msg % args' with severity 'WARNING'.

    To pass exception information, use the keyword argument exc_info with
    a true value, e.g.

    logger.warning("Houston, we have a %s", "bit of a problem", exc_info=1)
    """

    logger = get_logger()
    logger.warning(msg, *args, **kwargs)


def error(msg, *args, **kwargs):
    """
    Log 'msg % args' with severity 'ERROR'.

    To pass exception information, use the keyword argument exc_info with
    a true value, e.g.

    logger.error("Houston, we have a %s", "major problem", exc_info=1)
    """

    logger = get_logger()
    logger.error(msg, *args, **kwargs)


def critical(msg, *args, **kwargs):
    """
    Log 'msg % args' with severity 'CRITICAL'.

    To pass exception information, use the keyword argument exc_info with
    a true value, e.g.

    logger.critical("Houston, we have a %s", "major disaster", exc_info=1)
    """

    logger = get_logger()
    logger.critical(msg, *args, **kwargs)


def log(level, msg, *args, **kwargs):
    """
    Log 'msg % args' with the integer severity 'level'.

    To pass exception information, use the keyword argument exc_info with
    a true value, e.g.

    logger.log(level, "We have a %s", "mysterious problem", exc_info=1)
    """

    logger = get_logger()
    logger.log(level, msg, *args, **kwargs)
