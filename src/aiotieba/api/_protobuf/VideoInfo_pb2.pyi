from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class VideoInfo(_message.Message):
    __slots__ = ("video_url", "video_duration", "video_width", "video_height", "thumbnail_url", "play_count")
    VIDEO_URL_FIELD_NUMBER: _ClassVar[int]
    VIDEO_DURATION_FIELD_NUMBER: _ClassVar[int]
    VIDEO_WIDTH_FIELD_NUMBER: _ClassVar[int]
    VIDEO_HEIGHT_FIELD_NUMBER: _ClassVar[int]
    THUMBNAIL_URL_FIELD_NUMBER: _ClassVar[int]
    PLAY_COUNT_FIELD_NUMBER: _ClassVar[int]
    video_url: str
    video_duration: int
    video_width: int
    video_height: int
    thumbnail_url: str
    play_count: int
    def __init__(self, video_url: _Optional[str] = ..., video_duration: _Optional[int] = ..., video_width: _Optional[int] = ..., video_height: _Optional[int] = ..., thumbnail_url: _Optional[str] = ..., play_count: _Optional[int] = ...) -> None: ...
