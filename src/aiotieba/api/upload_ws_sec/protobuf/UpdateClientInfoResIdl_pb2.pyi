from ..._protobuf import Error_pb2 as _Error_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class UpdateClientInfoResIdl(_message.Message):
    __slots__ = ("error", "data")
    class DataRes(_message.Message):
        __slots__ = ("groupInfo", "userInfo", "isUserAvailable")
        class GroupInfo(_message.Message):
            __slots__ = ("groupId", "groupType", "lastMsgId")
            GROUPID_FIELD_NUMBER: _ClassVar[int]
            GROUPTYPE_FIELD_NUMBER: _ClassVar[int]
            LASTMSGID_FIELD_NUMBER: _ClassVar[int]
            groupId: int
            groupType: int
            lastMsgId: int
            def __init__(self, groupId: _Optional[int] = ..., groupType: _Optional[int] = ..., lastMsgId: _Optional[int] = ...) -> None: ...
        class UserInfo(_message.Message):
            __slots__ = ("userId", "userName", "portrait")
            USERID_FIELD_NUMBER: _ClassVar[int]
            USERNAME_FIELD_NUMBER: _ClassVar[int]
            PORTRAIT_FIELD_NUMBER: _ClassVar[int]
            userId: int
            userName: str
            portrait: str
            def __init__(self, userId: _Optional[int] = ..., userName: _Optional[str] = ..., portrait: _Optional[str] = ...) -> None: ...
        GROUPINFO_FIELD_NUMBER: _ClassVar[int]
        USERINFO_FIELD_NUMBER: _ClassVar[int]
        ISUSERAVAILABLE_FIELD_NUMBER: _ClassVar[int]
        groupInfo: _containers.RepeatedCompositeFieldContainer[UpdateClientInfoResIdl.DataRes.GroupInfo]
        userInfo: UpdateClientInfoResIdl.DataRes.UserInfo
        isUserAvailable: int
        def __init__(self, groupInfo: _Optional[_Iterable[_Union[UpdateClientInfoResIdl.DataRes.GroupInfo, _Mapping]]] = ..., userInfo: _Optional[_Union[UpdateClientInfoResIdl.DataRes.UserInfo, _Mapping]] = ..., isUserAvailable: _Optional[int] = ...) -> None: ...
    ERROR_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    error: _Error_pb2.Error
    data: UpdateClientInfoResIdl.DataRes
    def __init__(self, error: _Optional[_Union[_Error_pb2.Error, _Mapping]] = ..., data: _Optional[_Union[UpdateClientInfoResIdl.DataRes, _Mapping]] = ...) -> None: ...
