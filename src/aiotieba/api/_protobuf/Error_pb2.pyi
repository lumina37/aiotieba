from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class Error(_message.Message):
    __slots__ = ("errorno", "errmsg")
    ERRORNO_FIELD_NUMBER: _ClassVar[int]
    ERRMSG_FIELD_NUMBER: _ClassVar[int]
    errorno: int
    errmsg: str
    def __init__(self, errorno: _Optional[int] = ..., errmsg: _Optional[str] = ...) -> None: ...
