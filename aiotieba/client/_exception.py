from typing import Callable, Optional

TypeExceptionHandler = Callable[[Exception], Optional[Exception]]


class ExceptionHandlers(object):
    """
    异常处理
    """

    __slots__ = ['_handlers']

    def __init__(self) -> None:
        self._handlers = {}

    def get(self, meth: Callable, default: Optional[TypeExceptionHandler] = None) -> Optional[TypeExceptionHandler]:
        """
        获取用于处理某个特定方法中产生的所有异常的处理函数

        Args:
            meth (Callable): 类方法
            handler (TypeExceptionHandler): 处理函数 接收一个异常对象 返回异常对象或None
        """

        return self._handlers.get(meth.__name__, default)

    def __getitem__(self, meth: Callable) -> Optional[TypeExceptionHandler]:
        return self._handlers[meth.__name__]

    def __setitem__(self, meth: Callable, handler: TypeExceptionHandler) -> None:
        """
        设置用于处理某个特定方法中产生的所有异常的处理函数

        Args:
            meth (Callable): 类方法
            handler (TypeExceptionHandler): 处理函数 接收一个异常对象 返回异常对象或None
        """

        self._handlers[meth.__name__] = handler

    def _handle(self, meth_name: str, err: Exception) -> None:
        handler = self._handlers.get(meth_name, None)
        if handler:
            try:
                handler(err)
            except Exception as new_err:
                raise new_err from err


exc_handlers = ExceptionHandlers()


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

    __slots__ = ['code', 'msg']

    def __init__(self, code: int, msg: str) -> None:
        super().__init__(code, msg)
        self.code = code
        self.msg = msg


class TiebaValueError(RuntimeError):
    """
    意外的字段值
    """

    pass


class ContentTypeError(RuntimeError):
    """
    无法解析响应头中的content-type
    """
