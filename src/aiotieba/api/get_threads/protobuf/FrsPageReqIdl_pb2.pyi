from ..._protobuf import CommonReq_pb2 as _CommonReq_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class FrsPageReqIdl(_message.Message):
    __slots__ = ("data",)
    class DataReq(_message.Message):
        __slots__ = ("common", "kw", "rn", "rn_need", "is_good", "cid", "pn", "sort_type")
        COMMON_FIELD_NUMBER: _ClassVar[int]
        KW_FIELD_NUMBER: _ClassVar[int]
        RN_FIELD_NUMBER: _ClassVar[int]
        RN_NEED_FIELD_NUMBER: _ClassVar[int]
        IS_GOOD_FIELD_NUMBER: _ClassVar[int]
        CID_FIELD_NUMBER: _ClassVar[int]
        PN_FIELD_NUMBER: _ClassVar[int]
        SORT_TYPE_FIELD_NUMBER: _ClassVar[int]
        common: _CommonReq_pb2.CommonReq
        kw: str
        rn: int
        rn_need: int
        is_good: int
        cid: int
        pn: int
        sort_type: int
        def __init__(self, common: _Optional[_Union[_CommonReq_pb2.CommonReq, _Mapping]] = ..., kw: _Optional[str] = ..., rn: _Optional[int] = ..., rn_need: _Optional[int] = ..., is_good: _Optional[int] = ..., cid: _Optional[int] = ..., pn: _Optional[int] = ..., sort_type: _Optional[int] = ...) -> None: ...
    DATA_FIELD_NUMBER: _ClassVar[int]
    data: FrsPageReqIdl.DataReq
    def __init__(self, data: _Optional[_Union[FrsPageReqIdl.DataReq, _Mapping]] = ...) -> None: ...
