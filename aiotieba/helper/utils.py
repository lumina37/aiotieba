import asyncio
import functools
import logging
import sys
from datetime import datetime
from typing import Any, Callable, Optional

if sys.version_info >= (3, 11):
    import asyncio as async_timeout
else:
    import async_timeout

import json as jsonlib

from ..logging import get_logger

parse_json = jsonlib.loads
pack_json = functools.partial(jsonlib.dumps, separators=(',', ':'))

if sys.version_info >= (3, 9):
    import random

    randbytes_nosec = random.randbytes
else:
    import secrets

    randbytes_nosec = secrets.token_bytes

if sys.version_info >= (3, 9):

    def removeprefix(s: str, prefix: str) -> str:
        """
        移除字符串前缀

        Args:
            s (str): 待移除前缀的字符串
            prefix (str): 待移除的前缀

        Returns:
            str: 移除前缀后的字符串
        """

        return s.removeprefix(prefix)

    def removesuffix(s: str, suffix: str) -> str:
        """
        移除字符串前缀

        Args:
            s (str): 待移除前缀的字符串
            suffix (str): 待移除的前缀

        Returns:
            str: 移除前缀后的字符串
        """

        return s.removesuffix(suffix)

else:

    def removeprefix(s: str, prefix: str) -> str:
        """
        移除字符串前缀

        Args:
            s (str): 待移除前缀的字符串
            prefix (str): 待移除的前缀

        Returns:
            str: 移除前缀后的字符串

        Note:
            该函数不会拷贝字符串
        """

        if s.startswith(prefix):
            return s[len(prefix) :]
        else:
            return s

    def removesuffix(s: str, suffix: str) -> str:
        """
        移除字符串后缀
        该函数将不会拷贝字符串

        Args:
            s (str): 待移除前缀的字符串
            suffix (str): 待移除的前缀

        Returns:
            str: 移除前缀后的字符串

        Note:
            该函数不会拷贝字符串
        """

        if s.endswith(suffix):
            return s[: len(suffix)]
        else:
            return s


def is_portrait(portrait: str) -> bool:
    """
    简单判断输入是否符合portrait格式
    """

    return isinstance(portrait, str) and portrait.startswith('tb.')


def default_datetime() -> datetime:
    return datetime(1970, 1, 1)


def timeout(delay: float, loop: asyncio.AbstractEventLoop) -> async_timeout.Timeout:
    now = loop.time()
    when = round(now) + delay
    return async_timeout.timeout_at(when)


def handle_exception(
    null_factory: Callable[[], Any],
    ok_log_level: int = logging.NOTSET,
    err_log_level: int = logging.WARNING,
):
    """
    处理request抛出的异常 只能用于装饰类成员函数

    Args:
        null_factory (Callable[[], Any]): 空构造工厂 用于返回一个默认值
        ok_log_level (int, optional): 正常日志等级. Defaults to logging.NOTSET.
        err_log_level (int, optional): 异常日志等级. Defaults to logging.WARNING.
    """

    def wrapper(func):
        async def awrapper(*args, **kwargs):
            def _log(log_level: int, err: Optional[Exception] = None) -> None:
                logger = get_logger()
                if logger.isEnabledFor(err_log_level):
                    if err is None:
                        err = "Suceeded"
                    log_str = f"{err}. args={args[1:]} kwargs={kwargs}"
                    record = logger.makeRecord(logger.name, log_level, None, 0, log_str, None, None, func.__name__)
                    logger.handle(record)

            try:
                ret = await func(*args, **kwargs)

                if ok_log_level:
                    _log(ok_log_level)

            except Exception as err:
                _log(err_log_level, err)

                ret = null_factory()
                ret.err = err

                return ret

            else:
                return ret

        return awrapper

    return wrapper
