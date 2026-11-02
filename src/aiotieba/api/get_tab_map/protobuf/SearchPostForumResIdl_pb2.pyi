from ..._protobuf import Error_pb2 as _Error_pb2
from ..._protobuf import FrsTabInfo_pb2 as _FrsTabInfo_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class SearchPostForumResIdl(_message.Message):
    __slots__ = ("error", "data")
    class DataRes(_message.Message):
        __slots__ = ("exact_match",)
        class SearchForum(_message.Message):
            __slots__ = ("forum_id", "forum_name", "tab_info")
            FORUM_ID_FIELD_NUMBER: _ClassVar[int]
            FORUM_NAME_FIELD_NUMBER: _ClassVar[int]
            TAB_INFO_FIELD_NUMBER: _ClassVar[int]
            forum_id: int
            forum_name: str
            tab_info: _containers.RepeatedCompositeFieldContainer[_FrsTabInfo_pb2.FrsTabInfo]
            def __init__(self, forum_id: _Optional[int] = ..., forum_name: _Optional[str] = ..., tab_info: _Optional[_Iterable[_Union[_FrsTabInfo_pb2.FrsTabInfo, _Mapping]]] = ...) -> None: ...
        EXACT_MATCH_FIELD_NUMBER: _ClassVar[int]
        exact_match: SearchPostForumResIdl.DataRes.SearchForum
        def __init__(self, exact_match: _Optional[_Union[SearchPostForumResIdl.DataRes.SearchForum, _Mapping]] = ...) -> None: ...
    ERROR_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    error: _Error_pb2.Error
    data: SearchPostForumResIdl.DataRes
    def __init__(self, error: _Optional[_Union[_Error_pb2.Error, _Mapping]] = ..., data: _Optional[_Union[SearchPostForumResIdl.DataRes, _Mapping]] = ...) -> None: ...
