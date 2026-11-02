from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class CommitReceivedPmsgReqIdl(_message.Message):
    __slots__ = ("data",)
    class DataReq(_message.Message):
        __slots__ = ("groupId", "toUid", "msgType", "msgId")
        GROUPID_FIELD_NUMBER: _ClassVar[int]
        TOUID_FIELD_NUMBER: _ClassVar[int]
        MSGTYPE_FIELD_NUMBER: _ClassVar[int]
        MSGID_FIELD_NUMBER: _ClassVar[int]
        groupId: int
        toUid: int
        msgType: int
        msgId: int
        def __init__(self, groupId: _Optional[int] = ..., toUid: _Optional[int] = ..., msgType: _Optional[int] = ..., msgId: _Optional[int] = ...) -> None: ...
    DATA_FIELD_NUMBER: _ClassVar[int]
    data: CommitReceivedPmsgReqIdl.DataReq
    def __init__(self, data: _Optional[_Union[CommitReceivedPmsgReqIdl.DataReq, _Mapping]] = ...) -> None: ...
