from ..._protobuf import CommonReq_pb2 as _CommonReq_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class SearchPostForumReqIdl(_message.Message):
    __slots__ = ("data",)
    class DataReq(_message.Message):
        __slots__ = ("common", "fname")
        COMMON_FIELD_NUMBER: _ClassVar[int]
        FNAME_FIELD_NUMBER: _ClassVar[int]
        common: _CommonReq_pb2.CommonReq
        fname: str
        def __init__(self, common: _Optional[_Union[_CommonReq_pb2.CommonReq, _Mapping]] = ..., fname: _Optional[str] = ...) -> None: ...
    DATA_FIELD_NUMBER: _ClassVar[int]
    data: SearchPostForumReqIdl.DataReq
    def __init__(self, data: _Optional[_Union[SearchPostForumReqIdl.DataReq, _Mapping]] = ...) -> None: ...
