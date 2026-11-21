from ..._protobuf import Error_pb2 as _Error_pb2
from ..._protobuf import Page_pb2 as _Page_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GetForumSquareResIdl(_message.Message):
    __slots__ = ("error", "data")
    class DataRes(_message.Message):
        __slots__ = ("forum_info", "page")
        class RecommendForumInfo(_message.Message):
            __slots__ = ("forum_id", "forum_name", "is_like", "member_count", "thread_count")
            FORUM_ID_FIELD_NUMBER: _ClassVar[int]
            FORUM_NAME_FIELD_NUMBER: _ClassVar[int]
            IS_LIKE_FIELD_NUMBER: _ClassVar[int]
            MEMBER_COUNT_FIELD_NUMBER: _ClassVar[int]
            THREAD_COUNT_FIELD_NUMBER: _ClassVar[int]
            forum_id: int
            forum_name: str
            is_like: int
            member_count: int
            thread_count: int
            def __init__(self, forum_id: _Optional[int] = ..., forum_name: _Optional[str] = ..., is_like: _Optional[int] = ..., member_count: _Optional[int] = ..., thread_count: _Optional[int] = ...) -> None: ...
        FORUM_INFO_FIELD_NUMBER: _ClassVar[int]
        PAGE_FIELD_NUMBER: _ClassVar[int]
        forum_info: _containers.RepeatedCompositeFieldContainer[GetForumSquareResIdl.DataRes.RecommendForumInfo]
        page: _Page_pb2.Page
        def __init__(self, forum_info: _Optional[_Iterable[_Union[GetForumSquareResIdl.DataRes.RecommendForumInfo, _Mapping]]] = ..., page: _Optional[_Union[_Page_pb2.Page, _Mapping]] = ...) -> None: ...
    ERROR_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    error: _Error_pb2.Error
    data: GetForumSquareResIdl.DataRes
    def __init__(self, error: _Optional[_Union[_Error_pb2.Error, _Mapping]] = ..., data: _Optional[_Union[GetForumSquareResIdl.DataRes, _Mapping]] = ...) -> None: ...
