from ..._protobuf import Error_pb2 as _Error_pb2
from ..._protobuf import Page_pb2 as _Page_pb2
from ..._protobuf import ThreadInfo_pb2 as _ThreadInfo_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class FrsPageResIdl4lp(_message.Message):
    __slots__ = ("error", "data")
    class DataRes(_message.Message):
        __slots__ = ("forum", "page", "thread_list")
        class ForumInfo(_message.Message):
            __slots__ = ("id", "name")
            ID_FIELD_NUMBER: _ClassVar[int]
            NAME_FIELD_NUMBER: _ClassVar[int]
            id: int
            name: str
            def __init__(self, id: _Optional[int] = ..., name: _Optional[str] = ...) -> None: ...
        FORUM_FIELD_NUMBER: _ClassVar[int]
        PAGE_FIELD_NUMBER: _ClassVar[int]
        THREAD_LIST_FIELD_NUMBER: _ClassVar[int]
        forum: FrsPageResIdl4lp.DataRes.ForumInfo
        page: _Page_pb2.Page
        thread_list: _containers.RepeatedCompositeFieldContainer[_ThreadInfo_pb2.ThreadInfo]
        def __init__(self, forum: _Optional[_Union[FrsPageResIdl4lp.DataRes.ForumInfo, _Mapping]] = ..., page: _Optional[_Union[_Page_pb2.Page, _Mapping]] = ..., thread_list: _Optional[_Iterable[_Union[_ThreadInfo_pb2.ThreadInfo, _Mapping]]] = ...) -> None: ...
    ERROR_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    error: _Error_pb2.Error
    data: FrsPageResIdl4lp.DataRes
    def __init__(self, error: _Optional[_Union[_Error_pb2.Error, _Mapping]] = ..., data: _Optional[_Union[FrsPageResIdl4lp.DataRes, _Mapping]] = ...) -> None: ...
