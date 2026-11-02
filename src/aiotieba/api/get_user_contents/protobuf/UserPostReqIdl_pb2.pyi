from ..._protobuf import CommonReq_pb2 as _CommonReq_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class UserPostReqIdl(_message.Message):
    __slots__ = ("data",)
    class DataReq(_message.Message):
        __slots__ = ("uid", "rn", "is_thread", "need_content", "pn", "is_view_card", "common")
        UID_FIELD_NUMBER: _ClassVar[int]
        RN_FIELD_NUMBER: _ClassVar[int]
        IS_THREAD_FIELD_NUMBER: _ClassVar[int]
        NEED_CONTENT_FIELD_NUMBER: _ClassVar[int]
        PN_FIELD_NUMBER: _ClassVar[int]
        IS_VIEW_CARD_FIELD_NUMBER: _ClassVar[int]
        COMMON_FIELD_NUMBER: _ClassVar[int]
        uid: int
        rn: int
        is_thread: int
        need_content: int
        pn: int
        is_view_card: int
        common: _CommonReq_pb2.CommonReq
        def __init__(self, uid: _Optional[int] = ..., rn: _Optional[int] = ..., is_thread: _Optional[int] = ..., need_content: _Optional[int] = ..., pn: _Optional[int] = ..., is_view_card: _Optional[int] = ..., common: _Optional[_Union[_CommonReq_pb2.CommonReq, _Mapping]] = ...) -> None: ...
    DATA_FIELD_NUMBER: _ClassVar[int]
    data: UserPostReqIdl.DataReq
    def __init__(self, data: _Optional[_Union[UserPostReqIdl.DataReq, _Mapping]] = ...) -> None: ...
