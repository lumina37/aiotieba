from ..._protobuf import CommonReq_pb2 as _CommonReq_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class AddPollReqIdl(_message.Message):
    __slots__ = ("data",)
    class DataReq(_message.Message):
        __slots__ = ("thread_id", "options", "common", "forum_id")
        THREAD_ID_FIELD_NUMBER: _ClassVar[int]
        OPTIONS_FIELD_NUMBER: _ClassVar[int]
        COMMON_FIELD_NUMBER: _ClassVar[int]
        FORUM_ID_FIELD_NUMBER: _ClassVar[int]
        thread_id: int
        options: str
        common: _CommonReq_pb2.CommonReq
        forum_id: int
        def __init__(self, thread_id: _Optional[int] = ..., options: _Optional[str] = ..., common: _Optional[_Union[_CommonReq_pb2.CommonReq, _Mapping]] = ..., forum_id: _Optional[int] = ...) -> None: ...
    DATA_FIELD_NUMBER: _ClassVar[int]
    data: AddPollReqIdl.DataReq
    def __init__(self, data: _Optional[_Union[AddPollReqIdl.DataReq, _Mapping]] = ...) -> None: ...
