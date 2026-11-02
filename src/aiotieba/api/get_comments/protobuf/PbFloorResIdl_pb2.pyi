from ..._protobuf import Error_pb2 as _Error_pb2
from ..._protobuf import Page_pb2 as _Page_pb2
from ..._protobuf import Post_pb2 as _Post_pb2
from ..._protobuf import ThreadInfo_pb2 as _ThreadInfo_pb2
from ..._protobuf import SimpleForum_pb2 as _SimpleForum_pb2
from ..._protobuf import SubPostList_pb2 as _SubPostList_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class PbFloorResIdl(_message.Message):
    __slots__ = ("error", "data")
    class DataRes(_message.Message):
        __slots__ = ("page", "post", "subpost_list", "thread", "forum")
        PAGE_FIELD_NUMBER: _ClassVar[int]
        POST_FIELD_NUMBER: _ClassVar[int]
        SUBPOST_LIST_FIELD_NUMBER: _ClassVar[int]
        THREAD_FIELD_NUMBER: _ClassVar[int]
        FORUM_FIELD_NUMBER: _ClassVar[int]
        page: _Page_pb2.Page
        post: _Post_pb2.Post
        subpost_list: _containers.RepeatedCompositeFieldContainer[_SubPostList_pb2.SubPostList]
        thread: _ThreadInfo_pb2.ThreadInfo
        forum: _SimpleForum_pb2.SimpleForum
        def __init__(self, page: _Optional[_Union[_Page_pb2.Page, _Mapping]] = ..., post: _Optional[_Union[_Post_pb2.Post, _Mapping]] = ..., subpost_list: _Optional[_Iterable[_Union[_SubPostList_pb2.SubPostList, _Mapping]]] = ..., thread: _Optional[_Union[_ThreadInfo_pb2.ThreadInfo, _Mapping]] = ..., forum: _Optional[_Union[_SimpleForum_pb2.SimpleForum, _Mapping]] = ...) -> None: ...
    ERROR_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    error: _Error_pb2.Error
    data: PbFloorResIdl.DataRes
    def __init__(self, error: _Optional[_Union[_Error_pb2.Error, _Mapping]] = ..., data: _Optional[_Union[PbFloorResIdl.DataRes, _Mapping]] = ...) -> None: ...
