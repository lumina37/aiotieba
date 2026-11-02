from ..._protobuf import Error_pb2 as _Error_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class CommitReceivedPmsgResIdl(_message.Message):
    __slots__ = ("error", "data")
    class DataRes(_message.Message):
        __slots__ = ("readMsgId", "groupId", "toUid", "toUserType")
        READMSGID_FIELD_NUMBER: _ClassVar[int]
        GROUPID_FIELD_NUMBER: _ClassVar[int]
        TOUID_FIELD_NUMBER: _ClassVar[int]
        TOUSERTYPE_FIELD_NUMBER: _ClassVar[int]
        readMsgId: int
        groupId: int
        toUid: int
        toUserType: int
        def __init__(self, readMsgId: _Optional[int] = ..., groupId: _Optional[int] = ..., toUid: _Optional[int] = ..., toUserType: _Optional[int] = ...) -> None: ...
    ERROR_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    error: _Error_pb2.Error
    data: CommitReceivedPmsgResIdl.DataRes
    def __init__(self, error: _Optional[_Union[_Error_pb2.Error, _Mapping]] = ..., data: _Optional[_Union[CommitReceivedPmsgResIdl.DataRes, _Mapping]] = ...) -> None: ...
