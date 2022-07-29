__all__ = ['LOG']

import logging
import logging.handlers
import sys
from pathlib import Path
from typing import ClassVar, Union

LogLevel = Union[int, str]

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

    file_log_level: ClassVar[LogLevel] = logging.INFO
    console_log_level: ClassVar[LogLevel] = logging.DEBUG
    enable_file_log: ClassVar[bool] = True

    formatter: ClassVar[logging.Formatter] = logging.Formatter(
        "<{asctime}> [{levelname}] [{funcName}] {message}", style='{'
    )

    __slots__ = [
        '_file_hd',
        '_console_hd',
    ]

    def __init__(self, name: str) -> None:
        super().__init__(name)

        self._file_hd = None
        self._console_hd = None

        if self.enable_file_log:
            self.addHandler(self.file_hd)
        self.addHandler(self.console_hd)

    @property
    def file_hd(self) -> logging.handlers.TimedRotatingFileHandler:
        """
        指向log/xxx.log文件的日志handler
        """

        if self._file_hd is None:

            log_dir = Path("log")
            log_dir.mkdir(0o755, exist_ok=True)

            log_filepath = log_dir / f"{self.name}.log"
            self._file_hd = logging.handlers.TimedRotatingFileHandler(
                str(log_filepath), when='MIDNIGHT', backupCount=5, encoding='utf-8'
            )

            self._file_hd.setLevel(self.file_log_level)
            self._file_hd.setFormatter(self.formatter)

        return self._file_hd

    @property
    def console_hd(self) -> logging.StreamHandler:
        """
        指向标准输出流的日志handler
        """

        if self._console_hd is None:

            import sys

            self._console_hd = logging.StreamHandler(sys.stdout)

            self._console_hd.setLevel(self.console_log_level)
            self._console_hd.setFormatter(self.formatter)

        return self._console_hd


script_name = Path(sys.argv[0]).stem
LOG = TiebaLogger(script_name)
