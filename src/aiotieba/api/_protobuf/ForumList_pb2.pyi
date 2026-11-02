from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class ForumList(_message.Message):
    __slots__ = ("forum_id", "forum_name", "member_count", "post_num", "thread_num")
    FORUM_ID_FIELD_NUMBER: _ClassVar[int]
    FORUM_NAME_FIELD_NUMBER: _ClassVar[int]
    MEMBER_COUNT_FIELD_NUMBER: _ClassVar[int]
    POST_NUM_FIELD_NUMBER: _ClassVar[int]
    THREAD_NUM_FIELD_NUMBER: _ClassVar[int]
    forum_id: int
    forum_name: str
    member_count: int
    post_num: int
    thread_num: int
    def __init__(self, forum_id: _Optional[int] = ..., forum_name: _Optional[str] = ..., member_count: _Optional[int] = ..., post_num: _Optional[int] = ..., thread_num: _Optional[int] = ...) -> None: ...
