from ..._protobuf import Error_pb2 as _Error_pb2
from ..._protobuf import Page_pb2 as _Page_pb2
from ..._protobuf import ThreadInfo_pb2 as _ThreadInfo_pb2
from ..._protobuf import User_pb2 as _User_pb2
from ..._protobuf import FrsTabInfo_pb2 as _FrsTabInfo_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class FrsPageResIdl(_message.Message):
    __slots__ = ("error", "data")
    class DataRes(_message.Message):
        __slots__ = ("forum", "page", "thread_list", "user_list", "nav_tab_info", "forum_rule")
        class ForumInfo(_message.Message):
            __slots__ = ("id", "name", "first_class", "second_class", "member_num", "thread_num", "post_num", "managers")
            class Manager(_message.Message):
                __slots__ = ()
                def __init__(self) -> None: ...
            ID_FIELD_NUMBER: _ClassVar[int]
            NAME_FIELD_NUMBER: _ClassVar[int]
            FIRST_CLASS_FIELD_NUMBER: _ClassVar[int]
            SECOND_CLASS_FIELD_NUMBER: _ClassVar[int]
            MEMBER_NUM_FIELD_NUMBER: _ClassVar[int]
            THREAD_NUM_FIELD_NUMBER: _ClassVar[int]
            POST_NUM_FIELD_NUMBER: _ClassVar[int]
            MANAGERS_FIELD_NUMBER: _ClassVar[int]
            id: int
            name: str
            first_class: str
            second_class: str
            member_num: int
            thread_num: int
            post_num: int
            managers: _containers.RepeatedCompositeFieldContainer[FrsPageResIdl.DataRes.ForumInfo.Manager]
            def __init__(self, id: _Optional[int] = ..., name: _Optional[str] = ..., first_class: _Optional[str] = ..., second_class: _Optional[str] = ..., member_num: _Optional[int] = ..., thread_num: _Optional[int] = ..., post_num: _Optional[int] = ..., managers: _Optional[_Iterable[_Union[FrsPageResIdl.DataRes.ForumInfo.Manager, _Mapping]]] = ...) -> None: ...
        class NavTabInfo(_message.Message):
            __slots__ = ("tab",)
            TAB_FIELD_NUMBER: _ClassVar[int]
            tab: _containers.RepeatedCompositeFieldContainer[_FrsTabInfo_pb2.FrsTabInfo]
            def __init__(self, tab: _Optional[_Iterable[_Union[_FrsTabInfo_pb2.FrsTabInfo, _Mapping]]] = ...) -> None: ...
        class ForumRuleStatus(_message.Message):
            __slots__ = ("has_forum_rule",)
            HAS_FORUM_RULE_FIELD_NUMBER: _ClassVar[int]
            has_forum_rule: int
            def __init__(self, has_forum_rule: _Optional[int] = ...) -> None: ...
        FORUM_FIELD_NUMBER: _ClassVar[int]
        PAGE_FIELD_NUMBER: _ClassVar[int]
        THREAD_LIST_FIELD_NUMBER: _ClassVar[int]
        USER_LIST_FIELD_NUMBER: _ClassVar[int]
        NAV_TAB_INFO_FIELD_NUMBER: _ClassVar[int]
        FORUM_RULE_FIELD_NUMBER: _ClassVar[int]
        forum: FrsPageResIdl.DataRes.ForumInfo
        page: _Page_pb2.Page
        thread_list: _containers.RepeatedCompositeFieldContainer[_ThreadInfo_pb2.ThreadInfo]
        user_list: _containers.RepeatedCompositeFieldContainer[_User_pb2.User]
        nav_tab_info: FrsPageResIdl.DataRes.NavTabInfo
        forum_rule: FrsPageResIdl.DataRes.ForumRuleStatus
        def __init__(self, forum: _Optional[_Union[FrsPageResIdl.DataRes.ForumInfo, _Mapping]] = ..., page: _Optional[_Union[_Page_pb2.Page, _Mapping]] = ..., thread_list: _Optional[_Iterable[_Union[_ThreadInfo_pb2.ThreadInfo, _Mapping]]] = ..., user_list: _Optional[_Iterable[_Union[_User_pb2.User, _Mapping]]] = ..., nav_tab_info: _Optional[_Union[FrsPageResIdl.DataRes.NavTabInfo, _Mapping]] = ..., forum_rule: _Optional[_Union[FrsPageResIdl.DataRes.ForumRuleStatus, _Mapping]] = ...) -> None: ...
    ERROR_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    error: _Error_pb2.Error
    data: FrsPageResIdl.DataRes
    def __init__(self, error: _Optional[_Union[_Error_pb2.Error, _Mapping]] = ..., data: _Optional[_Union[FrsPageResIdl.DataRes, _Mapping]] = ...) -> None: ...
