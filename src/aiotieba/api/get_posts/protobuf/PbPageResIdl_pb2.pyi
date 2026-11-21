from ..._protobuf import Error_pb2 as _Error_pb2
from ..._protobuf import SimpleForum_pb2 as _SimpleForum_pb2
from ..._protobuf import Page_pb2 as _Page_pb2
from ..._protobuf import Post_pb2 as _Post_pb2
from ..._protobuf import ThreadInfo_pb2 as _ThreadInfo_pb2
from ..._protobuf import User_pb2 as _User_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class PbPageResIdl(_message.Message):
    __slots__ = ("error", "data")
    class DataRes(_message.Message):
        __slots__ = ("forum", "page", "post_list", "thread", "user_list", "thread_freq_num")
        FORUM_FIELD_NUMBER: _ClassVar[int]
        PAGE_FIELD_NUMBER: _ClassVar[int]
        POST_LIST_FIELD_NUMBER: _ClassVar[int]
        THREAD_FIELD_NUMBER: _ClassVar[int]
        USER_LIST_FIELD_NUMBER: _ClassVar[int]
        THREAD_FREQ_NUM_FIELD_NUMBER: _ClassVar[int]
        forum: _SimpleForum_pb2.SimpleForum
        page: _Page_pb2.Page
        post_list: _containers.RepeatedCompositeFieldContainer[_Post_pb2.Post]
        thread: _ThreadInfo_pb2.ThreadInfo
        user_list: _containers.RepeatedCompositeFieldContainer[_User_pb2.User]
        thread_freq_num: int
        def __init__(self, forum: _Optional[_Union[_SimpleForum_pb2.SimpleForum, _Mapping]] = ..., page: _Optional[_Union[_Page_pb2.Page, _Mapping]] = ..., post_list: _Optional[_Iterable[_Union[_Post_pb2.Post, _Mapping]]] = ..., thread: _Optional[_Union[_ThreadInfo_pb2.ThreadInfo, _Mapping]] = ..., user_list: _Optional[_Iterable[_Union[_User_pb2.User, _Mapping]]] = ..., thread_freq_num: _Optional[int] = ...) -> None: ...
    ERROR_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    error: _Error_pb2.Error
    data: PbPageResIdl.DataRes
    def __init__(self, error: _Optional[_Union[_Error_pb2.Error, _Mapping]] = ..., data: _Optional[_Union[PbPageResIdl.DataRes, _Mapping]] = ...) -> None: ...
