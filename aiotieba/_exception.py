import dataclasses


@dataclasses.dataclass(eq=False)
class TiebaServerError(RuntimeError):
    """
    贴吧服务器异常
    """

    code: int
    msg: str


class ContentTypeError(RuntimeError):
    """
    无法解析响应头中的content-type
    """
