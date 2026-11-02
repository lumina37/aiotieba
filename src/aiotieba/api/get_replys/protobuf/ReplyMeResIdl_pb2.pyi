from ..._protobuf import Error_pb2 as _Error_pb2
from ..._protobuf import Page_pb2 as _Page_pb2
from ..._protobuf import PbContent_pb2 as _PbContent_pb2
from ..._protobuf import User_pb2 as _User_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ReplyMeResIdl(_message.Message):
    __slots__ = ("error", "data")
    class DataRes(_message.Message):
        __slots__ = ("page", "reply_list")
        class ReplyList(_message.Message):
            __slots__ = ("thread_id", "post_id", "time", "fname", "content", "is_floor", "quote_content", "replyer", "quote_pid", "quote_user", "thread_author_user", "new_floor_info")
            class NewFloorInfo(_message.Message):
                __slots__ = ("content",)
                CONTENT_FIELD_NUMBER: _ClassVar[int]
                content: _containers.RepeatedCompositeFieldContainer[_PbContent_pb2.PbContent]
                def __init__(self, content: _Optional[_Iterable[_Union[_PbContent_pb2.PbContent, _Mapping]]] = ...) -> None: ...
            THREAD_ID_FIELD_NUMBER: _ClassVar[int]
            POST_ID_FIELD_NUMBER: _ClassVar[int]
            TIME_FIELD_NUMBER: _ClassVar[int]
            FNAME_FIELD_NUMBER: _ClassVar[int]
            CONTENT_FIELD_NUMBER: _ClassVar[int]
            IS_FLOOR_FIELD_NUMBER: _ClassVar[int]
            QUOTE_CONTENT_FIELD_NUMBER: _ClassVar[int]
            REPLYER_FIELD_NUMBER: _ClassVar[int]
            QUOTE_PID_FIELD_NUMBER: _ClassVar[int]
            QUOTE_USER_FIELD_NUMBER: _ClassVar[int]
            THREAD_AUTHOR_USER_FIELD_NUMBER: _ClassVar[int]
            NEW_FLOOR_INFO_FIELD_NUMBER: _ClassVar[int]
            thread_id: int
            post_id: int
            time: int
            fname: str
            content: str
            is_floor: int
            quote_content: str
            replyer: _User_pb2.User
            quote_pid: int
            quote_user: _User_pb2.User
            thread_author_user: _User_pb2.User
            new_floor_info: _containers.RepeatedCompositeFieldContainer[ReplyMeResIdl.DataRes.ReplyList.NewFloorInfo]
            def __init__(self, thread_id: _Optional[int] = ..., post_id: _Optional[int] = ..., time: _Optional[int] = ..., fname: _Optional[str] = ..., content: _Optional[str] = ..., is_floor: _Optional[int] = ..., quote_content: _Optional[str] = ..., replyer: _Optional[_Union[_User_pb2.User, _Mapping]] = ..., quote_pid: _Optional[int] = ..., quote_user: _Optional[_Union[_User_pb2.User, _Mapping]] = ..., thread_author_user: _Optional[_Union[_User_pb2.User, _Mapping]] = ..., new_floor_info: _Optional[_Iterable[_Union[ReplyMeResIdl.DataRes.ReplyList.NewFloorInfo, _Mapping]]] = ...) -> None: ...
        PAGE_FIELD_NUMBER: _ClassVar[int]
        REPLY_LIST_FIELD_NUMBER: _ClassVar[int]
        page: _Page_pb2.Page
        reply_list: _containers.RepeatedCompositeFieldContainer[ReplyMeResIdl.DataRes.ReplyList]
        def __init__(self, page: _Optional[_Union[_Page_pb2.Page, _Mapping]] = ..., reply_list: _Optional[_Iterable[_Union[ReplyMeResIdl.DataRes.ReplyList, _Mapping]]] = ...) -> None: ...
    ERROR_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    error: _Error_pb2.Error
    data: ReplyMeResIdl.DataRes
    def __init__(self, error: _Optional[_Union[_Error_pb2.Error, _Mapping]] = ..., data: _Optional[_Union[ReplyMeResIdl.DataRes, _Mapping]] = ...) -> None: ...
