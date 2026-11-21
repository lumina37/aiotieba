from ..._protobuf import Error_pb2 as _Error_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GetGroupMsgResIdl(_message.Message):
    __slots__ = ("error", "data")
    class DataRes(_message.Message):
        __slots__ = ("groupInfo",)
        class GroupMsg(_message.Message):
            __slots__ = ("groupInfo", "msgList")
            class GroupInfo(_message.Message):
                __slots__ = ("groupId", "groupType")
                GROUPID_FIELD_NUMBER: _ClassVar[int]
                GROUPTYPE_FIELD_NUMBER: _ClassVar[int]
                groupId: int
                groupType: int
                def __init__(self, groupId: _Optional[int] = ..., groupType: _Optional[int] = ...) -> None: ...
            class MsgInfo(_message.Message):
                __slots__ = ("msgId", "msgType", "content", "createTime", "userInfo")
                class UserInfo(_message.Message):
                    __slots__ = ("userId", "userName", "portrait")
                    USERID_FIELD_NUMBER: _ClassVar[int]
                    USERNAME_FIELD_NUMBER: _ClassVar[int]
                    PORTRAIT_FIELD_NUMBER: _ClassVar[int]
                    userId: int
                    userName: str
                    portrait: str
                    def __init__(self, userId: _Optional[int] = ..., userName: _Optional[str] = ..., portrait: _Optional[str] = ...) -> None: ...
                MSGID_FIELD_NUMBER: _ClassVar[int]
                MSGTYPE_FIELD_NUMBER: _ClassVar[int]
                CONTENT_FIELD_NUMBER: _ClassVar[int]
                CREATETIME_FIELD_NUMBER: _ClassVar[int]
                USERINFO_FIELD_NUMBER: _ClassVar[int]
                msgId: int
                msgType: int
                content: str
                createTime: int
                userInfo: GetGroupMsgResIdl.DataRes.GroupMsg.MsgInfo.UserInfo
                def __init__(self, msgId: _Optional[int] = ..., msgType: _Optional[int] = ..., content: _Optional[str] = ..., createTime: _Optional[int] = ..., userInfo: _Optional[_Union[GetGroupMsgResIdl.DataRes.GroupMsg.MsgInfo.UserInfo, _Mapping]] = ...) -> None: ...
            GROUPINFO_FIELD_NUMBER: _ClassVar[int]
            MSGLIST_FIELD_NUMBER: _ClassVar[int]
            groupInfo: GetGroupMsgResIdl.DataRes.GroupMsg.GroupInfo
            msgList: _containers.RepeatedCompositeFieldContainer[GetGroupMsgResIdl.DataRes.GroupMsg.MsgInfo]
            def __init__(self, groupInfo: _Optional[_Union[GetGroupMsgResIdl.DataRes.GroupMsg.GroupInfo, _Mapping]] = ..., msgList: _Optional[_Iterable[_Union[GetGroupMsgResIdl.DataRes.GroupMsg.MsgInfo, _Mapping]]] = ...) -> None: ...
        GROUPINFO_FIELD_NUMBER: _ClassVar[int]
        groupInfo: _containers.RepeatedCompositeFieldContainer[GetGroupMsgResIdl.DataRes.GroupMsg]
        def __init__(self, groupInfo: _Optional[_Iterable[_Union[GetGroupMsgResIdl.DataRes.GroupMsg, _Mapping]]] = ...) -> None: ...
    ERROR_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    error: _Error_pb2.Error
    data: GetGroupMsgResIdl.DataRes
    def __init__(self, error: _Optional[_Union[_Error_pb2.Error, _Mapping]] = ..., data: _Optional[_Union[GetGroupMsgResIdl.DataRes, _Mapping]] = ...) -> None: ...
