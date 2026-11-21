from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class SimpleForum(_message.Message):
    __slots__ = ("id", "name", "first_class", "second_class", "member_num", "post_num")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    FIRST_CLASS_FIELD_NUMBER: _ClassVar[int]
    SECOND_CLASS_FIELD_NUMBER: _ClassVar[int]
    MEMBER_NUM_FIELD_NUMBER: _ClassVar[int]
    POST_NUM_FIELD_NUMBER: _ClassVar[int]
    id: int
    name: str
    first_class: str
    second_class: str
    member_num: int
    post_num: int
    def __init__(self, id: _Optional[int] = ..., name: _Optional[str] = ..., first_class: _Optional[str] = ..., second_class: _Optional[str] = ..., member_num: _Optional[int] = ..., post_num: _Optional[int] = ...) -> None: ...
