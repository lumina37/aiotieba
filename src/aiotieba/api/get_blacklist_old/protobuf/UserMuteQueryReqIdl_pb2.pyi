from ..._protobuf import CommonReq_pb2 as _CommonReq_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class UserMuteQueryReqIdl(_message.Message):
    __slots__ = ("data",)
    class DataReq(_message.Message):
        __slots__ = ("common", "pn", "rn")
        COMMON_FIELD_NUMBER: _ClassVar[int]
        PN_FIELD_NUMBER: _ClassVar[int]
        RN_FIELD_NUMBER: _ClassVar[int]
        common: _CommonReq_pb2.CommonReq
        pn: int
        rn: int
        def __init__(self, common: _Optional[_Union[_CommonReq_pb2.CommonReq, _Mapping]] = ..., pn: _Optional[int] = ..., rn: _Optional[int] = ...) -> None: ...
    DATA_FIELD_NUMBER: _ClassVar[int]
    data: UserMuteQueryReqIdl.DataReq
    def __init__(self, data: _Optional[_Union[UserMuteQueryReqIdl.DataReq, _Mapping]] = ...) -> None: ...
