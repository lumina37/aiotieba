from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class FrsTabInfo(_message.Message):
    __slots__ = ("tab_id", "tab_name")
    TAB_ID_FIELD_NUMBER: _ClassVar[int]
    TAB_NAME_FIELD_NUMBER: _ClassVar[int]
    tab_id: int
    tab_name: str
    def __init__(self, tab_id: _Optional[int] = ..., tab_name: _Optional[str] = ...) -> None: ...
