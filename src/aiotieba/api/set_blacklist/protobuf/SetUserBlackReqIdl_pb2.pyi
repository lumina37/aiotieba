from ..._protobuf import CommonReq_pb2 as _CommonReq_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class SetUserBlackReqIdl(_message.Message):
    __slots__ = ("data",)
    class DataReq(_message.Message):
        __slots__ = ("common", "black_uid", "perm_list")
        class PermissionList(_message.Message):
            __slots__ = ("follow", "interact", "chat")
            FOLLOW_FIELD_NUMBER: _ClassVar[int]
            INTERACT_FIELD_NUMBER: _ClassVar[int]
            CHAT_FIELD_NUMBER: _ClassVar[int]
            follow: int
            interact: int
            chat: int
            def __init__(self, follow: _Optional[int] = ..., interact: _Optional[int] = ..., chat: _Optional[int] = ...) -> None: ...
        COMMON_FIELD_NUMBER: _ClassVar[int]
        BLACK_UID_FIELD_NUMBER: _ClassVar[int]
        PERM_LIST_FIELD_NUMBER: _ClassVar[int]
        common: _CommonReq_pb2.CommonReq
        black_uid: int
        perm_list: SetUserBlackReqIdl.DataReq.PermissionList
        def __init__(self, common: _Optional[_Union[_CommonReq_pb2.CommonReq, _Mapping]] = ..., black_uid: _Optional[int] = ..., perm_list: _Optional[_Union[SetUserBlackReqIdl.DataReq.PermissionList, _Mapping]] = ...) -> None: ...
    DATA_FIELD_NUMBER: _ClassVar[int]
    data: SetUserBlackReqIdl.DataReq
    def __init__(self, data: _Optional[_Union[SetUserBlackReqIdl.DataReq, _Mapping]] = ...) -> None: ...
