from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class PollInfo(_message.Message):
    __slots__ = ("is_multi", "total_num", "options", "total_poll", "title")
    class PollOption(_message.Message):
        __slots__ = ("num", "text")
        NUM_FIELD_NUMBER: _ClassVar[int]
        TEXT_FIELD_NUMBER: _ClassVar[int]
        num: int
        text: str
        def __init__(self, num: _Optional[int] = ..., text: _Optional[str] = ...) -> None: ...
    IS_MULTI_FIELD_NUMBER: _ClassVar[int]
    TOTAL_NUM_FIELD_NUMBER: _ClassVar[int]
    OPTIONS_FIELD_NUMBER: _ClassVar[int]
    TOTAL_POLL_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    is_multi: int
    total_num: int
    options: _containers.RepeatedCompositeFieldContainer[PollInfo.PollOption]
    total_poll: int
    title: str
    def __init__(self, is_multi: _Optional[int] = ..., total_num: _Optional[int] = ..., options: _Optional[_Iterable[_Union[PollInfo.PollOption, _Mapping]]] = ..., total_poll: _Optional[int] = ..., title: _Optional[str] = ...) -> None: ...
