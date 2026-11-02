from ..._protobuf import CommonReq_pb2 as _CommonReq_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GetBawuInfoReqIdl(_message.Message):
    __slots__ = ("data",)
    class DataReq(_message.Message):
        __slots__ = ("common", "fid")
        COMMON_FIELD_NUMBER: _ClassVar[int]
        FID_FIELD_NUMBER: _ClassVar[int]
        common: _CommonReq_pb2.CommonReq
        fid: int
        def __init__(self, common: _Optional[_Union[_CommonReq_pb2.CommonReq, _Mapping]] = ..., fid: _Optional[int] = ...) -> None: ...
    DATA_FIELD_NUMBER: _ClassVar[int]
    data: GetBawuInfoReqIdl.DataReq
    def __init__(self, data: _Optional[_Union[GetBawuInfoReqIdl.DataReq, _Mapping]] = ...) -> None: ...
