from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GetGroupMsgReqIdl(_message.Message):
    __slots__ = ("cuid", "data")
    class DataReq(_message.Message):
        __slots__ = ("groupMids", "gettype")
        class GroupLastId(_message.Message):
            __slots__ = ("groupId", "lastMsgId")
            GROUPID_FIELD_NUMBER: _ClassVar[int]
            LASTMSGID_FIELD_NUMBER: _ClassVar[int]
            groupId: int
            lastMsgId: int
            def __init__(self, groupId: _Optional[int] = ..., lastMsgId: _Optional[int] = ...) -> None: ...
        GROUPMIDS_FIELD_NUMBER: _ClassVar[int]
        GETTYPE_FIELD_NUMBER: _ClassVar[int]
        groupMids: _containers.RepeatedCompositeFieldContainer[GetGroupMsgReqIdl.DataReq.GroupLastId]
        gettype: str
        def __init__(self, groupMids: _Optional[_Iterable[_Union[GetGroupMsgReqIdl.DataReq.GroupLastId, _Mapping]]] = ..., gettype: _Optional[str] = ...) -> None: ...
    CUID_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    cuid: str
    data: GetGroupMsgReqIdl.DataReq
    def __init__(self, cuid: _Optional[str] = ..., data: _Optional[_Union[GetGroupMsgReqIdl.DataReq, _Mapping]] = ...) -> None: ...
