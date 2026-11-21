from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GetUserInfoReqIdl(_message.Message):
    __slots__ = ("data",)
    class DataReq(_message.Message):
        __slots__ = ("user_id",)
        USER_ID_FIELD_NUMBER: _ClassVar[int]
        user_id: int
        def __init__(self, user_id: _Optional[int] = ...) -> None: ...
    DATA_FIELD_NUMBER: _ClassVar[int]
    data: GetUserInfoReqIdl.DataReq
    def __init__(self, data: _Optional[_Union[GetUserInfoReqIdl.DataReq, _Mapping]] = ...) -> None: ...
