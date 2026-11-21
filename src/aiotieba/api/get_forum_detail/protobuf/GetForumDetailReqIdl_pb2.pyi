from ..._protobuf import CommonReq_pb2 as _CommonReq_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GetForumDetailReqIdl(_message.Message):
    __slots__ = ("data",)
    class DataReq(_message.Message):
        __slots__ = ("forum_id", "common")
        FORUM_ID_FIELD_NUMBER: _ClassVar[int]
        COMMON_FIELD_NUMBER: _ClassVar[int]
        forum_id: int
        common: _CommonReq_pb2.CommonReq
        def __init__(self, forum_id: _Optional[int] = ..., common: _Optional[_Union[_CommonReq_pb2.CommonReq, _Mapping]] = ...) -> None: ...
    DATA_FIELD_NUMBER: _ClassVar[int]
    data: GetForumDetailReqIdl.DataReq
    def __init__(self, data: _Optional[_Union[GetForumDetailReqIdl.DataReq, _Mapping]] = ...) -> None: ...
