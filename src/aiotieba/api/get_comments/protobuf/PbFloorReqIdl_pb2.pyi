from ..._protobuf import CommonReq_pb2 as _CommonReq_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class PbFloorReqIdl(_message.Message):
    __slots__ = ("data",)
    class DataReq(_message.Message):
        __slots__ = ("common", "kz", "pid", "spid", "pn", "sort")
        COMMON_FIELD_NUMBER: _ClassVar[int]
        KZ_FIELD_NUMBER: _ClassVar[int]
        PID_FIELD_NUMBER: _ClassVar[int]
        SPID_FIELD_NUMBER: _ClassVar[int]
        PN_FIELD_NUMBER: _ClassVar[int]
        SORT_FIELD_NUMBER: _ClassVar[int]
        common: _CommonReq_pb2.CommonReq
        kz: int
        pid: int
        spid: int
        pn: int
        sort: int
        def __init__(self, common: _Optional[_Union[_CommonReq_pb2.CommonReq, _Mapping]] = ..., kz: _Optional[int] = ..., pid: _Optional[int] = ..., spid: _Optional[int] = ..., pn: _Optional[int] = ..., sort: _Optional[int] = ...) -> None: ...
    DATA_FIELD_NUMBER: _ClassVar[int]
    data: PbFloorReqIdl.DataReq
    def __init__(self, data: _Optional[_Union[PbFloorReqIdl.DataReq, _Mapping]] = ...) -> None: ...
