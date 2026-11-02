from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class Agree(_message.Message):
    __slots__ = ("agree_num", "disagree_num")
    AGREE_NUM_FIELD_NUMBER: _ClassVar[int]
    DISAGREE_NUM_FIELD_NUMBER: _ClassVar[int]
    agree_num: int
    disagree_num: int
    def __init__(self, agree_num: _Optional[int] = ..., disagree_num: _Optional[int] = ...) -> None: ...
