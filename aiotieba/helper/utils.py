import asyncio
import functools
import logging
import sys
from types import FrameType
from typing import Any, Callable

import async_timeout

from ..exception import exc_handlers
from ..logging import get_logger

try:
    import simdjson as jsonlib

    _JSON_PARSER = jsonlib.Parser()
    parse_json = _JSON_PARSER.parse

except ImportError:
    import json as jsonlib

    parse_json = jsonlib.loads

pack_json = functools.partial(jsonlib.dumps, separators=(',', ':'))

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


def timeout(delay: float, loop: asyncio.AbstractEventLoop) -> async_timeout.Timeout:
    now = loop.time()
    when = round(now) + delay
    return async_timeout.timeout_at(when)


def log_success(frame: FrameType, log_str: str = '', log_level: int = logging.INFO):
    """
    成功日志

    Args:
        frame (FrameType): 帧对象
        log_str (str): 附加日志
        log_level (int): 日志等级
    """

    meth_name = frame.f_code.co_name
    log_str = "Suceeded. " + log_str
    logger = get_logger()
    if logger.isEnabledFor(log_level):
        record = logger.makeRecord(logger.name, log_level, None, 0, log_str, None, None, meth_name)
        logger.handle(record)


def handle_exception(null_ret_factory: Callable[[], Any], no_format: bool = False, log_level: int = logging.WARNING):
    """
    处理request抛出的异常

    Args:
        null_ret_factory (Callable[[], Any]): 空构造工厂 用于返回一个默认值
        no_format (bool, optional): 不需要再次格式化日志字符串 常见于不论成功与否都会记录日志的api. Defaults to False.
        log_level (int, optional): 日志等级. Defaults to logging.WARNING.
    """

    def wrapper(func):
        async def awrapper(*args, **kwargs):
            try:
                ret = await func(*args, **kwargs)

            except Exception as err:
                meth_name = func.__name__
                tb = err.__traceback__
                while tb := tb.tb_next:
                    frame = tb.tb_frame
                    if frame.f_code.co_name == meth_name:
                        break
                frame = tb.tb_next.tb_frame

                log_str: str = frame.f_locals.get('__log__', '')
                if not no_format:  # need format
                    log_str = log_str.format(**frame.f_locals)
                log_str = f"{err}. {log_str}"

                logger = get_logger()
                if logger.isEnabledFor(log_level):
                    record = logger.makeRecord(logger.name, log_level, None, 0, log_str, None, None, meth_name)
                    logger.handle(record)

                exc_handlers._handle(meth_name, err)

                return null_ret_factory()

            else:
                return ret

        return awrapper

    return wrapper
