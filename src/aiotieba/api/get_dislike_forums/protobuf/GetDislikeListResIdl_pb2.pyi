from ..._protobuf import Error_pb2 as _Error_pb2
from ..._protobuf import ForumList_pb2 as _ForumList_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GetDislikeListResIdl(_message.Message):
    __slots__ = ("error", "data")
    class DataRes(_message.Message):
        __slots__ = ("forum_list", "has_more", "cur_page")
        FORUM_LIST_FIELD_NUMBER: _ClassVar[int]
        HAS_MORE_FIELD_NUMBER: _ClassVar[int]
        CUR_PAGE_FIELD_NUMBER: _ClassVar[int]
        forum_list: _containers.RepeatedCompositeFieldContainer[_ForumList_pb2.ForumList]
        has_more: int
        cur_page: int
        def __init__(self, forum_list: _Optional[_Iterable[_Union[_ForumList_pb2.ForumList, _Mapping]]] = ..., has_more: _Optional[int] = ..., cur_page: _Optional[int] = ...) -> None: ...
    ERROR_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    error: _Error_pb2.Error
    data: GetDislikeListResIdl.DataRes
    def __init__(self, error: _Optional[_Union[_Error_pb2.Error, _Mapping]] = ..., data: _Optional[_Union[GetDislikeListResIdl.DataRes, _Mapping]] = ...) -> None: ...
