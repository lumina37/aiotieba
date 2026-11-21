from . import Media_pb2 as _Media_pb2
from . import Voice_pb2 as _Voice_pb2
from . import PollInfo_pb2 as _PollInfo_pb2
from . import VideoInfo_pb2 as _VideoInfo_pb2
from . import PbContent_pb2 as _PbContent_pb2
from . import Agree_pb2 as _Agree_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class PostInfoList(_message.Message):
    __slots__ = ("forum_id", "thread_id", "post_id", "create_time", "forum_name", "title", "content", "user_name", "media", "reply_num", "user_id", "user_portrait", "voice_info", "thread_type", "poll_info", "video_info", "freq_num", "name_show", "share_num", "agree", "is_share_thread", "first_post_content")
    class PostInfoContent(_message.Message):
        __slots__ = ("post_content", "create_time", "post_type", "post_id")
        class Abstract(_message.Message):
            __slots__ = ("type", "text", "link", "src", "un", "during_time", "voice_md5")
            TYPE_FIELD_NUMBER: _ClassVar[int]
            TEXT_FIELD_NUMBER: _ClassVar[int]
            LINK_FIELD_NUMBER: _ClassVar[int]
            SRC_FIELD_NUMBER: _ClassVar[int]
            UN_FIELD_NUMBER: _ClassVar[int]
            DURING_TIME_FIELD_NUMBER: _ClassVar[int]
            VOICE_MD5_FIELD_NUMBER: _ClassVar[int]
            type: int
            text: str
            link: str
            src: str
            un: str
            during_time: str
            voice_md5: str
            def __init__(self, type: _Optional[int] = ..., text: _Optional[str] = ..., link: _Optional[str] = ..., src: _Optional[str] = ..., un: _Optional[str] = ..., during_time: _Optional[str] = ..., voice_md5: _Optional[str] = ...) -> None: ...
        POST_CONTENT_FIELD_NUMBER: _ClassVar[int]
        CREATE_TIME_FIELD_NUMBER: _ClassVar[int]
        POST_TYPE_FIELD_NUMBER: _ClassVar[int]
        POST_ID_FIELD_NUMBER: _ClassVar[int]
        post_content: _containers.RepeatedCompositeFieldContainer[PostInfoList.PostInfoContent.Abstract]
        create_time: int
        post_type: int
        post_id: int
        def __init__(self, post_content: _Optional[_Iterable[_Union[PostInfoList.PostInfoContent.Abstract, _Mapping]]] = ..., create_time: _Optional[int] = ..., post_type: _Optional[int] = ..., post_id: _Optional[int] = ...) -> None: ...
    FORUM_ID_FIELD_NUMBER: _ClassVar[int]
    THREAD_ID_FIELD_NUMBER: _ClassVar[int]
    POST_ID_FIELD_NUMBER: _ClassVar[int]
    CREATE_TIME_FIELD_NUMBER: _ClassVar[int]
    FORUM_NAME_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    USER_NAME_FIELD_NUMBER: _ClassVar[int]
    MEDIA_FIELD_NUMBER: _ClassVar[int]
    REPLY_NUM_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    USER_PORTRAIT_FIELD_NUMBER: _ClassVar[int]
    VOICE_INFO_FIELD_NUMBER: _ClassVar[int]
    THREAD_TYPE_FIELD_NUMBER: _ClassVar[int]
    POLL_INFO_FIELD_NUMBER: _ClassVar[int]
    VIDEO_INFO_FIELD_NUMBER: _ClassVar[int]
    FREQ_NUM_FIELD_NUMBER: _ClassVar[int]
    NAME_SHOW_FIELD_NUMBER: _ClassVar[int]
    SHARE_NUM_FIELD_NUMBER: _ClassVar[int]
    AGREE_FIELD_NUMBER: _ClassVar[int]
    IS_SHARE_THREAD_FIELD_NUMBER: _ClassVar[int]
    FIRST_POST_CONTENT_FIELD_NUMBER: _ClassVar[int]
    forum_id: int
    thread_id: int
    post_id: int
    create_time: int
    forum_name: str
    title: str
    content: _containers.RepeatedCompositeFieldContainer[PostInfoList.PostInfoContent]
    user_name: str
    media: _containers.RepeatedCompositeFieldContainer[_Media_pb2.Media]
    reply_num: int
    user_id: int
    user_portrait: str
    voice_info: _containers.RepeatedCompositeFieldContainer[_Voice_pb2.Voice]
    thread_type: int
    poll_info: _PollInfo_pb2.PollInfo
    video_info: _VideoInfo_pb2.VideoInfo
    freq_num: int
    name_show: str
    share_num: int
    agree: _Agree_pb2.Agree
    is_share_thread: int
    first_post_content: _containers.RepeatedCompositeFieldContainer[_PbContent_pb2.PbContent]
    def __init__(self, forum_id: _Optional[int] = ..., thread_id: _Optional[int] = ..., post_id: _Optional[int] = ..., create_time: _Optional[int] = ..., forum_name: _Optional[str] = ..., title: _Optional[str] = ..., content: _Optional[_Iterable[_Union[PostInfoList.PostInfoContent, _Mapping]]] = ..., user_name: _Optional[str] = ..., media: _Optional[_Iterable[_Union[_Media_pb2.Media, _Mapping]]] = ..., reply_num: _Optional[int] = ..., user_id: _Optional[int] = ..., user_portrait: _Optional[str] = ..., voice_info: _Optional[_Iterable[_Union[_Voice_pb2.Voice, _Mapping]]] = ..., thread_type: _Optional[int] = ..., poll_info: _Optional[_Union[_PollInfo_pb2.PollInfo, _Mapping]] = ..., video_info: _Optional[_Union[_VideoInfo_pb2.VideoInfo, _Mapping]] = ..., freq_num: _Optional[int] = ..., name_show: _Optional[str] = ..., share_num: _Optional[int] = ..., agree: _Optional[_Union[_Agree_pb2.Agree, _Mapping]] = ..., is_share_thread: _Optional[int] = ..., first_post_content: _Optional[_Iterable[_Union[_PbContent_pb2.PbContent, _Mapping]]] = ...) -> None: ...
