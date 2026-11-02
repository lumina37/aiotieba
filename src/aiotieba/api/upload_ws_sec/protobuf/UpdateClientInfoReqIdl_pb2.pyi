from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class UpdateClientInfoReqIdl(_message.Message):
    __slots__ = ("cuid", "data")
    class DataReq(_message.Message):
        __slots__ = ("bduss", "device", "secretKey", "stoken")
        BDUSS_FIELD_NUMBER: _ClassVar[int]
        DEVICE_FIELD_NUMBER: _ClassVar[int]
        SECRETKEY_FIELD_NUMBER: _ClassVar[int]
        STOKEN_FIELD_NUMBER: _ClassVar[int]
        bduss: str
        device: str
        secretKey: bytes
        stoken: str
        def __init__(self, bduss: _Optional[str] = ..., device: _Optional[str] = ..., secretKey: _Optional[bytes] = ..., stoken: _Optional[str] = ...) -> None: ...
    CUID_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    cuid: str
    data: UpdateClientInfoReqIdl.DataReq
    def __init__(self, cuid: _Optional[str] = ..., data: _Optional[_Union[UpdateClientInfoReqIdl.DataReq, _Mapping]] = ...) -> None: ...
