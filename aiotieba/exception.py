import dataclasses as dcs
from typing import Optional


@dcs.dataclass
class TbErrorExt:
    """
    为类型添加一个`err`项 用于保存捕获到的异常
    """

    err: Optional[Exception] = None


@dcs.dataclass
class TbResponse(TbErrorExt):
    """
    bool返回值

    Attributes:
        err (Exception | None): 捕获的异常
    """

    def __bool__(self) -> bool:
        return self.err is None

    def __int__(self) -> int:
        return int(bool(self))


class TiebaServerError(RuntimeError):
    """
    贴吧服务器异常
    """

    __slots__ = ['code', 'msg']

    def __init__(self, code: int, msg: str) -> None:
        super().__init__(code, msg)
        self.code = code
        self.msg = msg


class HTTPStatusError(RuntimeError):
    """
    错误的状态码
    """

    __slots__ = ['code', 'msg']

    def __init__(self, code: int, msg: str) -> None:
        super().__init__(code, msg)
        self.code = code
        self.msg = msg


class TiebaValueError(RuntimeError):
    """
    意外的字段值
    """


class ContentTypeError(RuntimeError):
    """
    无法解析响应头中的content-type
    """
