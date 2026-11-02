from ..._protobuf import Error_pb2 as _Error_pb2
from ..._protobuf import Page_pb2 as _Page_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class UserMuteQueryResIdl(_message.Message):
    __slots__ = ("data", "error")
    class DataRes(_message.Message):
        __slots__ = ("mute_user", "page")
        class MuteUser(_message.Message):
            __slots__ = ("user_id", "user_name", "mute_time", "portrait", "name_show")
            USER_ID_FIELD_NUMBER: _ClassVar[int]
            USER_NAME_FIELD_NUMBER: _ClassVar[int]
            MUTE_TIME_FIELD_NUMBER: _ClassVar[int]
            PORTRAIT_FIELD_NUMBER: _ClassVar[int]
            NAME_SHOW_FIELD_NUMBER: _ClassVar[int]
            user_id: int
            user_name: str
            mute_time: int
            portrait: str
            name_show: str
            def __init__(self, user_id: _Optional[int] = ..., user_name: _Optional[str] = ..., mute_time: _Optional[int] = ..., portrait: _Optional[str] = ..., name_show: _Optional[str] = ...) -> None: ...
        MUTE_USER_FIELD_NUMBER: _ClassVar[int]
        PAGE_FIELD_NUMBER: _ClassVar[int]
        mute_user: _containers.RepeatedCompositeFieldContainer[UserMuteQueryResIdl.DataRes.MuteUser]
        page: _Page_pb2.Page
        def __init__(self, mute_user: _Optional[_Iterable[_Union[UserMuteQueryResIdl.DataRes.MuteUser, _Mapping]]] = ..., page: _Optional[_Union[_Page_pb2.Page, _Mapping]] = ...) -> None: ...
    DATA_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    data: UserMuteQueryResIdl.DataRes
    error: _Error_pb2.Error
    def __init__(self, data: _Optional[_Union[UserMuteQueryResIdl.DataRes, _Mapping]] = ..., error: _Optional[_Union[_Error_pb2.Error, _Mapping]] = ...) -> None: ...
