"""
日志记录

提供与标准库logging签名一致的六个函数debug/info/warning/error/critical/log
允许使用set_logger更换日志记录器
允许使用set_formatter更换日志记录器
"""

import logging
import logging.handlers
import sys
from pathlib import Path

logging.addLevelName(logging.FATAL, "FATAL")
logging.addLevelName(logging.WARN, "WARN")

logging.logThreads = False
logging.logProcesses = False
logging.logMultiprocessing = False
logging.raiseExceptions = False
logging.Formatter.default_msec_format = '%s.%03d'

_LOGGER = None
_FORMATTER = logging.Formatter("<{asctime}> [{levelname}] [{funcName}] {message}", style='{')


class TiebaLogger(logging.Logger):
    """
    日志记录器

    Args:
        name (str): 日志文件名(不含扩展名) 留空则自动设置为sys.argv[0]的文件名. Defaults to ''.
        file_log_level (int): 文件日志级别. Defaults to logging.INFO.
        stream_log_level (int): 标准输出日志级别. Defaults to logging.DEBUG.
        log_dir (int): 日志输出文件夹. Defaults to 'log'.
        backup_count (int): 时间轮转文件日志的保留文件数. Defaults to 5.
    """

    def __init__(
        self,
        name: str = '',
        *,
        file_log_level: int = logging.INFO,
        stream_log_level: int = logging.DEBUG,
        log_dir: str = 'log',
        backup_count: int = 5,
    ) -> None:

        if name == '':
            name = Path(sys.argv[0]).stem
        super().__init__(name)

        Path(log_dir).mkdir(0o755, exist_ok=True)

        file_hd = logging.handlers.TimedRotatingFileHandler(
            f"log/{self.name}.log", when='MIDNIGHT', backupCount=backup_count, encoding='utf-8'
        )
        file_hd.setLevel(file_log_level)
        file_hd.setFormatter(_FORMATTER)
        self.addHandler(file_hd)

        stream_hd = logging.StreamHandler(sys.stdout)
        stream_hd.setLevel(stream_log_level)
        stream_hd.setFormatter(_FORMATTER)
        self.addHandler(stream_hd)


def get_logger() -> TiebaLogger:
    global _LOGGER

    if _LOGGER is None:
        _LOGGER = TiebaLogger()

    return _LOGGER


def set_logger(logger: logging.Logger) -> None:
    """
    更换aiotieba的日志记录器

    Args:
        logger (logging.Logger)
    """

    global _LOGGER
    _LOGGER = logger


def set_formatter(formatter: logging.Formatter) -> None:
    """
    更换aiotieba的日志格式

    Args:
        formatter (logging.Formatter)
    """

    global _FORMATTER
    _FORMATTER = formatter

    if _LOGGER is not None:
        for hd in _LOGGER.handlers:
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
