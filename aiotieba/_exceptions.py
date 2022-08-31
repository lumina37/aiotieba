class TiebaServerError(RuntimeError):
    """
    贴吧服务器异常
    """


class ContentTypeError(RuntimeError):
    """
    无法解析响应头中的content-type
    """
