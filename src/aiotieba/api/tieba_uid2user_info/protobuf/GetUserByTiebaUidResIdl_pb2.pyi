from ..._protobuf import Error_pb2 as _Error_pb2
from ..._protobuf import User_pb2 as _User_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GetUserByTiebaUidResIdl(_message.Message):
    __slots__ = ("error", "data")
    class DataRes(_message.Message):
        __slots__ = ("user",)
        USER_FIELD_NUMBER: _ClassVar[int]
        user: _User_pb2.User
        def __init__(self, user: _Optional[_Union[_User_pb2.User, _Mapping]] = ...) -> None: ...
    ERROR_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    error: _Error_pb2.Error
    data: GetUserByTiebaUidResIdl.DataRes
    def __init__(self, error: _Optional[_Union[_Error_pb2.Error, _Mapping]] = ..., data: _Optional[_Union[GetUserByTiebaUidResIdl.DataRes, _Mapping]] = ...) -> None: ...
