from ..._protobuf import CommonReq_pb2 as _CommonReq_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ProfileReqIdl(_message.Message):
    __slots__ = ("data",)
    class DataReq(_message.Message):
        __slots__ = ("uid", "need_post_count", "pn", "common", "page", "friend_uid_portrait")
        UID_FIELD_NUMBER: _ClassVar[int]
        NEED_POST_COUNT_FIELD_NUMBER: _ClassVar[int]
        PN_FIELD_NUMBER: _ClassVar[int]
        COMMON_FIELD_NUMBER: _ClassVar[int]
        PAGE_FIELD_NUMBER: _ClassVar[int]
        FRIEND_UID_PORTRAIT_FIELD_NUMBER: _ClassVar[int]
        uid: int
        need_post_count: int
        pn: int
        common: _CommonReq_pb2.CommonReq
        page: int
        friend_uid_portrait: str
        def __init__(self, uid: _Optional[int] = ..., need_post_count: _Optional[int] = ..., pn: _Optional[int] = ..., common: _Optional[_Union[_CommonReq_pb2.CommonReq, _Mapping]] = ..., page: _Optional[int] = ..., friend_uid_portrait: _Optional[str] = ...) -> None: ...
    DATA_FIELD_NUMBER: _ClassVar[int]
    data: ProfileReqIdl.DataReq
    def __init__(self, data: _Optional[_Union[ProfileReqIdl.DataReq, _Mapping]] = ...) -> None: ...
