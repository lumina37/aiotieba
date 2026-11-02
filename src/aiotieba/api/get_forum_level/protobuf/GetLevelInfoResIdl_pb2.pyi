from ..._protobuf import Error_pb2 as _Error_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GetLevelInfoResIdl(_message.Message):
    __slots__ = ("error", "data")
    class DataRes(_message.Message):
        __slots__ = ("is_like", "level_name", "user_level")
        IS_LIKE_FIELD_NUMBER: _ClassVar[int]
        LEVEL_NAME_FIELD_NUMBER: _ClassVar[int]
        USER_LEVEL_FIELD_NUMBER: _ClassVar[int]
        is_like: int
        level_name: str
        user_level: int
        def __init__(self, is_like: _Optional[int] = ..., level_name: _Optional[str] = ..., user_level: _Optional[int] = ...) -> None: ...
    ERROR_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    error: _Error_pb2.Error
    data: GetLevelInfoResIdl.DataRes
    def __init__(self, error: _Optional[_Union[_Error_pb2.Error, _Mapping]] = ..., data: _Optional[_Union[GetLevelInfoResIdl.DataRes, _Mapping]] = ...) -> None: ...
