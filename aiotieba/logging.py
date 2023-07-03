import logging
import logging.handlers
import sys
from pathlib import Path

logging.addLevelName(logging.FATAL, "FATAL")
logging.addLevelName(logging.WARN, "WARN")

logging.logThreads = False
logging.logMultiprocessing = False
logging.raiseExceptions = False
logging.Formatter.default_msec_format = '%s.%03d'

_FORMATTER = logging.Formatter("<{asctime}> [{levelname}] [{funcName}] {message}", style='{')


class TiebaLogger(logging.Logger):
    """
    日志记录器

    Args:
        name (str): 日志文件名(不含扩展名) 留空则自动设置为`sys.argv[0]`的文件名. Defaults to ''.
        stream_log_level (int): 标准输出日志级别. Defaults to `logging.DEBUG`.
    """

    def __init__(self, name: str = '', stream_log_level: int = logging.DEBUG) -> None:
        if name == '':
            name = Path(sys.argv[0]).stem
        super().__init__(name)

        stream_hd = logging.StreamHandler(sys.stdout)
        stream_hd.setLevel(stream_log_level)
        stream_hd.setFormatter(_FORMATTER)
        self.addHandler(stream_hd)


_LOGGER = TiebaLogger()


def get_logger() -> TiebaLogger:
    """
    获取日志记录器

    Returns:
        TiebaLogger
    """

    global _LOGGER

    if _LOGGER is None:
        _LOGGER = TiebaLogger()

    return _LOGGER


def set_logger(new_logger: logging.Logger) -> None:
    """
    更换aiotieba的日志记录器

    Args:
        new_logger (logging.Logger): 新日志记录器
    """

    global _LOGGER
    _LOGGER = new_logger


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


def enableFileLog(log_level: int = logging.INFO, log_dir: Path = Path('log'), backup_count: int = 5) -> None:
    """
    启用文件日志

    Args:
        log_level (int): 文件日志级别. Defaults to `logging.INFO`.
        log_dir (Path): 用于存放日志文件的文件夹. Defaults to Path('log').
        backup_count (int): 时间轮转文件日志的保留文件数. Defaults to 5.
    """

    Path(log_dir).mkdir(0o755, exist_ok=True)

    file_hd = logging.handlers.TimedRotatingFileHandler(
        f"log/{_LOGGER.name}.log", when='MIDNIGHT', backupCount=backup_count, encoding='utf-8'
    )
    file_hd.setLevel(log_level)
    file_hd.setFormatter(_FORMATTER)
    _LOGGER.addHandler(file_hd)
