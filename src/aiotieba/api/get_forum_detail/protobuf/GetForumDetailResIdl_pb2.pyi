from ..._protobuf import Error_pb2 as _Error_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GetForumDetailResIdl(_message.Message):
    __slots__ = ("error", "data")
    class DataRes(_message.Message):
        __slots__ = ("forum_info", "election_tab")
        class RecommendForumInfo(_message.Message):
            __slots__ = ("avatar", "forum_id", "forum_name", "member_count", "thread_count", "slogan", "lv1_name", "avatar_origin")
            AVATAR_FIELD_NUMBER: _ClassVar[int]
            FORUM_ID_FIELD_NUMBER: _ClassVar[int]
            FORUM_NAME_FIELD_NUMBER: _ClassVar[int]
            MEMBER_COUNT_FIELD_NUMBER: _ClassVar[int]
            THREAD_COUNT_FIELD_NUMBER: _ClassVar[int]
            SLOGAN_FIELD_NUMBER: _ClassVar[int]
            LV1_NAME_FIELD_NUMBER: _ClassVar[int]
            AVATAR_ORIGIN_FIELD_NUMBER: _ClassVar[int]
            avatar: str
            forum_id: int
            forum_name: str
            member_count: int
            thread_count: int
            slogan: str
            lv1_name: str
            avatar_origin: str
            def __init__(self, avatar: _Optional[str] = ..., forum_id: _Optional[int] = ..., forum_name: _Optional[str] = ..., member_count: _Optional[int] = ..., thread_count: _Optional[int] = ..., slogan: _Optional[str] = ..., lv1_name: _Optional[str] = ..., avatar_origin: _Optional[str] = ...) -> None: ...
        class ManagerElectionTab(_message.Message):
            __slots__ = ("new_strategy_text",)
            NEW_STRATEGY_TEXT_FIELD_NUMBER: _ClassVar[int]
            new_strategy_text: str
            def __init__(self, new_strategy_text: _Optional[str] = ...) -> None: ...
        FORUM_INFO_FIELD_NUMBER: _ClassVar[int]
        ELECTION_TAB_FIELD_NUMBER: _ClassVar[int]
        forum_info: GetForumDetailResIdl.DataRes.RecommendForumInfo
        election_tab: GetForumDetailResIdl.DataRes.ManagerElectionTab
        def __init__(self, forum_info: _Optional[_Union[GetForumDetailResIdl.DataRes.RecommendForumInfo, _Mapping]] = ..., election_tab: _Optional[_Union[GetForumDetailResIdl.DataRes.ManagerElectionTab, _Mapping]] = ...) -> None: ...
    ERROR_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    error: _Error_pb2.Error
    data: GetForumDetailResIdl.DataRes
    def __init__(self, error: _Optional[_Union[_Error_pb2.Error, _Mapping]] = ..., data: _Optional[_Union[GetForumDetailResIdl.DataRes, _Mapping]] = ...) -> None: ...
