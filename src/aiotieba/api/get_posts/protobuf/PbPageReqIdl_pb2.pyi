from ..._protobuf import CommonReq_pb2 as _CommonReq_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class PbPageReqIdl(_message.Message):
    __slots__ = ("data",)
    class DataReq(_message.Message):
        __slots__ = ("common", "kz", "lz", "r", "pid", "with_floor", "floor_rn", "rn", "pn", "floor_sort_type")
        COMMON_FIELD_NUMBER: _ClassVar[int]
        KZ_FIELD_NUMBER: _ClassVar[int]
        LZ_FIELD_NUMBER: _ClassVar[int]
        R_FIELD_NUMBER: _ClassVar[int]
        PID_FIELD_NUMBER: _ClassVar[int]
        WITH_FLOOR_FIELD_NUMBER: _ClassVar[int]
        FLOOR_RN_FIELD_NUMBER: _ClassVar[int]
        RN_FIELD_NUMBER: _ClassVar[int]
        PN_FIELD_NUMBER: _ClassVar[int]
        FLOOR_SORT_TYPE_FIELD_NUMBER: _ClassVar[int]
        common: _CommonReq_pb2.CommonReq
        kz: int
        lz: int
        r: int
        pid: int
        with_floor: int
        floor_rn: int
        rn: int
        pn: int
        floor_sort_type: int
        def __init__(self, common: _Optional[_Union[_CommonReq_pb2.CommonReq, _Mapping]] = ..., kz: _Optional[int] = ..., lz: _Optional[int] = ..., r: _Optional[int] = ..., pid: _Optional[int] = ..., with_floor: _Optional[int] = ..., floor_rn: _Optional[int] = ..., rn: _Optional[int] = ..., pn: _Optional[int] = ..., floor_sort_type: _Optional[int] = ...) -> None: ...
    DATA_FIELD_NUMBER: _ClassVar[int]
    data: PbPageReqIdl.DataReq
    def __init__(self, data: _Optional[_Union[PbPageReqIdl.DataReq, _Mapping]] = ...) -> None: ...
