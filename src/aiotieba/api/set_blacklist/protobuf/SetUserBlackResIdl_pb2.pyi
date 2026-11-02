from ..._protobuf import Error_pb2 as _Error_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class SetUserBlackResIdl(_message.Message):
    __slots__ = ("error",)
    ERROR_FIELD_NUMBER: _ClassVar[int]
    error: _Error_pb2.Error
    def __init__(self, error: _Optional[_Union[_Error_pb2.Error, _Mapping]] = ...) -> None: ...
