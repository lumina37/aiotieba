from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class PushNotifyResIdl(_message.Message):
    __slots__ = ("multiMsg",)
    class PusherMsg(_message.Message):
        __slots__ = ("data",)
        class PusherMsgInfo(_message.Message):
            __slots__ = ("groupId", "msgId", "type", "et", "groupType")
            GROUPID_FIELD_NUMBER: _ClassVar[int]
            MSGID_FIELD_NUMBER: _ClassVar[int]
            TYPE_FIELD_NUMBER: _ClassVar[int]
            ET_FIELD_NUMBER: _ClassVar[int]
            GROUPTYPE_FIELD_NUMBER: _ClassVar[int]
            groupId: int
            msgId: int
            type: int
            et: str
            groupType: int
            def __init__(self, groupId: _Optional[int] = ..., msgId: _Optional[int] = ..., type: _Optional[int] = ..., et: _Optional[str] = ..., groupType: _Optional[int] = ...) -> None: ...
        DATA_FIELD_NUMBER: _ClassVar[int]
        data: PushNotifyResIdl.PusherMsg.PusherMsgInfo
        def __init__(self, data: _Optional[_Union[PushNotifyResIdl.PusherMsg.PusherMsgInfo, _Mapping]] = ...) -> None: ...
    MULTIMSG_FIELD_NUMBER: _ClassVar[int]
    multiMsg: _containers.RepeatedCompositeFieldContainer[PushNotifyResIdl.PusherMsg]
    def __init__(self, multiMsg: _Optional[_Iterable[_Union[PushNotifyResIdl.PusherMsg, _Mapping]]] = ...) -> None: ...
