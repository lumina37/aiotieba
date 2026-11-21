from ..._protobuf import CommonReq_pb2 as _CommonReq_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ReplyMeReqIdl(_message.Message):
    __slots__ = ("data",)
    class DataReq(_message.Message):
        __slots__ = ("pn", "common")
        PN_FIELD_NUMBER: _ClassVar[int]
        COMMON_FIELD_NUMBER: _ClassVar[int]
        pn: int
        common: _CommonReq_pb2.CommonReq
        def __init__(self, pn: _Optional[int] = ..., common: _Optional[_Union[_CommonReq_pb2.CommonReq, _Mapping]] = ...) -> None: ...
    DATA_FIELD_NUMBER: _ClassVar[int]
    data: ReplyMeReqIdl.DataReq
    def __init__(self, data: _Optional[_Union[ReplyMeReqIdl.DataReq, _Mapping]] = ...) -> None: ...
