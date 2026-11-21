from ..._protobuf import Error_pb2 as _Error_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class CommitPersonalMsgResIdl(_message.Message):
    __slots__ = ("error", "data")
    class DataRes(_message.Message):
        __slots__ = ("msgId", "groupId", "recordId", "toUid", "toUserType", "blockInfo")
        class BlockInfo(_message.Message):
            __slots__ = ("blockErrno", "blockErrmsg")
            BLOCKERRNO_FIELD_NUMBER: _ClassVar[int]
            BLOCKERRMSG_FIELD_NUMBER: _ClassVar[int]
            blockErrno: int
            blockErrmsg: str
            def __init__(self, blockErrno: _Optional[int] = ..., blockErrmsg: _Optional[str] = ...) -> None: ...
        MSGID_FIELD_NUMBER: _ClassVar[int]
        GROUPID_FIELD_NUMBER: _ClassVar[int]
        RECORDID_FIELD_NUMBER: _ClassVar[int]
        TOUID_FIELD_NUMBER: _ClassVar[int]
        TOUSERTYPE_FIELD_NUMBER: _ClassVar[int]
        BLOCKINFO_FIELD_NUMBER: _ClassVar[int]
        msgId: int
        groupId: int
        recordId: int
        toUid: int
        toUserType: int
        blockInfo: CommitPersonalMsgResIdl.DataRes.BlockInfo
        def __init__(self, msgId: _Optional[int] = ..., groupId: _Optional[int] = ..., recordId: _Optional[int] = ..., toUid: _Optional[int] = ..., toUserType: _Optional[int] = ..., blockInfo: _Optional[_Union[CommitPersonalMsgResIdl.DataRes.BlockInfo, _Mapping]] = ...) -> None: ...
    ERROR_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    error: _Error_pb2.Error
    data: CommitPersonalMsgResIdl.DataRes
    def __init__(self, error: _Optional[_Union[_Error_pb2.Error, _Mapping]] = ..., data: _Optional[_Union[CommitPersonalMsgResIdl.DataRes, _Mapping]] = ...) -> None: ...
