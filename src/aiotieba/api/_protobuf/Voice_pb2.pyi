from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class Voice(_message.Message):
    __slots__ = ("during_time", "voice_md5")
    DURING_TIME_FIELD_NUMBER: _ClassVar[int]
    VOICE_MD5_FIELD_NUMBER: _ClassVar[int]
    during_time: int
    voice_md5: str
    def __init__(self, during_time: _Optional[int] = ..., voice_md5: _Optional[str] = ...) -> None: ...
