from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class CommitPersonalMsgReqIdl(_message.Message):
    __slots__ = ("data",)
    class DataReq(_message.Message):
        __slots__ = ("toUid", "msgType", "content", "recordId")
        TOUID_FIELD_NUMBER: _ClassVar[int]
        MSGTYPE_FIELD_NUMBER: _ClassVar[int]
        CONTENT_FIELD_NUMBER: _ClassVar[int]
        RECORDID_FIELD_NUMBER: _ClassVar[int]
        toUid: int
        msgType: int
        content: str
        recordId: int
        def __init__(self, toUid: _Optional[int] = ..., msgType: _Optional[int] = ..., content: _Optional[str] = ..., recordId: _Optional[int] = ...) -> None: ...
    DATA_FIELD_NUMBER: _ClassVar[int]
    data: CommitPersonalMsgReqIdl.DataReq
    def __init__(self, data: _Optional[_Union[CommitPersonalMsgReqIdl.DataReq, _Mapping]] = ...) -> None: ...
