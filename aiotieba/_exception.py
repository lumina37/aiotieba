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
    非200状态码
    """


class ContentTypeError(RuntimeError):
    """
    无法解析响应头中的content-type
    """
