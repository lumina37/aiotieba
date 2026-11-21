from . import User_pb2 as _User_pb2
from . import Voice_pb2 as _Voice_pb2
from . import PollInfo_pb2 as _PollInfo_pb2
from . import VideoInfo_pb2 as _VideoInfo_pb2
from . import PbContent_pb2 as _PbContent_pb2
from . import Agree_pb2 as _Agree_pb2
from . import Media_pb2 as _Media_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ThreadInfo(_message.Message):
    __slots__ = ("id", "title", "reply_num", "view_num", "last_time_int", "is_top", "is_good", "is_voice_thread", "author", "last_replyer", "voice_info", "thread_type", "fid", "fname", "is_livepost", "first_post_id", "create_time", "post_id", "author_id", "valid_post_num", "is_ad", "poll_info", "video_info", "agree", "share_num", "origin_thread_info", "first_post_content", "is_share_thread", "tab_id", "is_deleted", "collect_num", "is_frs_mask")
    class OriginThreadInfo(_message.Message):
        __slots__ = ("title", "media", "fname", "tid", "fid", "thread_type", "is_deleted", "voice_info", "video_info", "content", "reply_num", "author", "agree", "shared_num", "poll_info", "pid")
        TITLE_FIELD_NUMBER: _ClassVar[int]
        MEDIA_FIELD_NUMBER: _ClassVar[int]
        FNAME_FIELD_NUMBER: _ClassVar[int]
        TID_FIELD_NUMBER: _ClassVar[int]
        FID_FIELD_NUMBER: _ClassVar[int]
        THREAD_TYPE_FIELD_NUMBER: _ClassVar[int]
        IS_DELETED_FIELD_NUMBER: _ClassVar[int]
        VOICE_INFO_FIELD_NUMBER: _ClassVar[int]
        VIDEO_INFO_FIELD_NUMBER: _ClassVar[int]
        CONTENT_FIELD_NUMBER: _ClassVar[int]
        REPLY_NUM_FIELD_NUMBER: _ClassVar[int]
        AUTHOR_FIELD_NUMBER: _ClassVar[int]
        AGREE_FIELD_NUMBER: _ClassVar[int]
        SHARED_NUM_FIELD_NUMBER: _ClassVar[int]
        POLL_INFO_FIELD_NUMBER: _ClassVar[int]
        PID_FIELD_NUMBER: _ClassVar[int]
        title: str
        media: _containers.RepeatedCompositeFieldContainer[_Media_pb2.Media]
        fname: str
        tid: str
        fid: int
        thread_type: int
        is_deleted: int
        voice_info: _containers.RepeatedCompositeFieldContainer[_Voice_pb2.Voice]
        video_info: _VideoInfo_pb2.VideoInfo
        content: _containers.RepeatedCompositeFieldContainer[_PbContent_pb2.PbContent]
        reply_num: int
        author: _User_pb2.User
        agree: _Agree_pb2.Agree
        shared_num: int
        poll_info: _PollInfo_pb2.PollInfo
        pid: int
        def __init__(self, title: _Optional[str] = ..., media: _Optional[_Iterable[_Union[_Media_pb2.Media, _Mapping]]] = ..., fname: _Optional[str] = ..., tid: _Optional[str] = ..., fid: _Optional[int] = ..., thread_type: _Optional[int] = ..., is_deleted: _Optional[int] = ..., voice_info: _Optional[_Iterable[_Union[_Voice_pb2.Voice, _Mapping]]] = ..., video_info: _Optional[_Union[_VideoInfo_pb2.VideoInfo, _Mapping]] = ..., content: _Optional[_Iterable[_Union[_PbContent_pb2.PbContent, _Mapping]]] = ..., reply_num: _Optional[int] = ..., author: _Optional[_Union[_User_pb2.User, _Mapping]] = ..., agree: _Optional[_Union[_Agree_pb2.Agree, _Mapping]] = ..., shared_num: _Optional[int] = ..., poll_info: _Optional[_Union[_PollInfo_pb2.PollInfo, _Mapping]] = ..., pid: _Optional[int] = ...) -> None: ...
    ID_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    REPLY_NUM_FIELD_NUMBER: _ClassVar[int]
    VIEW_NUM_FIELD_NUMBER: _ClassVar[int]
    LAST_TIME_INT_FIELD_NUMBER: _ClassVar[int]
    IS_TOP_FIELD_NUMBER: _ClassVar[int]
    IS_GOOD_FIELD_NUMBER: _ClassVar[int]
    IS_VOICE_THREAD_FIELD_NUMBER: _ClassVar[int]
    AUTHOR_FIELD_NUMBER: _ClassVar[int]
    LAST_REPLYER_FIELD_NUMBER: _ClassVar[int]
    VOICE_INFO_FIELD_NUMBER: _ClassVar[int]
    THREAD_TYPE_FIELD_NUMBER: _ClassVar[int]
    FID_FIELD_NUMBER: _ClassVar[int]
    FNAME_FIELD_NUMBER: _ClassVar[int]
    IS_LIVEPOST_FIELD_NUMBER: _ClassVar[int]
    FIRST_POST_ID_FIELD_NUMBER: _ClassVar[int]
    CREATE_TIME_FIELD_NUMBER: _ClassVar[int]
    POST_ID_FIELD_NUMBER: _ClassVar[int]
    AUTHOR_ID_FIELD_NUMBER: _ClassVar[int]
    VALID_POST_NUM_FIELD_NUMBER: _ClassVar[int]
    IS_AD_FIELD_NUMBER: _ClassVar[int]
    POLL_INFO_FIELD_NUMBER: _ClassVar[int]
    VIDEO_INFO_FIELD_NUMBER: _ClassVar[int]
    AGREE_FIELD_NUMBER: _ClassVar[int]
    SHARE_NUM_FIELD_NUMBER: _ClassVar[int]
    ORIGIN_THREAD_INFO_FIELD_NUMBER: _ClassVar[int]
    FIRST_POST_CONTENT_FIELD_NUMBER: _ClassVar[int]
    IS_SHARE_THREAD_FIELD_NUMBER: _ClassVar[int]
    TAB_ID_FIELD_NUMBER: _ClassVar[int]
    IS_DELETED_FIELD_NUMBER: _ClassVar[int]
    COLLECT_NUM_FIELD_NUMBER: _ClassVar[int]
    IS_FRS_MASK_FIELD_NUMBER: _ClassVar[int]
    id: int
    title: str
    reply_num: int
    view_num: int
    last_time_int: int
    is_top: int
    is_good: int
    is_voice_thread: int
    author: _User_pb2.User
    last_replyer: _User_pb2.User
    voice_info: _containers.RepeatedCompositeFieldContainer[_Voice_pb2.Voice]
    thread_type: int
    fid: int
    fname: str
    is_livepost: int
    first_post_id: int
    create_time: int
    post_id: int
    author_id: int
    valid_post_num: int
    is_ad: int
    poll_info: _PollInfo_pb2.PollInfo
    video_info: _VideoInfo_pb2.VideoInfo
    agree: _Agree_pb2.Agree
    share_num: int
    origin_thread_info: ThreadInfo.OriginThreadInfo
    first_post_content: _containers.RepeatedCompositeFieldContainer[_PbContent_pb2.PbContent]
    is_share_thread: int
    tab_id: int
    is_deleted: int
    collect_num: int
    is_frs_mask: int
    def __init__(self, id: _Optional[int] = ..., title: _Optional[str] = ..., reply_num: _Optional[int] = ..., view_num: _Optional[int] = ..., last_time_int: _Optional[int] = ..., is_top: _Optional[int] = ..., is_good: _Optional[int] = ..., is_voice_thread: _Optional[int] = ..., author: _Optional[_Union[_User_pb2.User, _Mapping]] = ..., last_replyer: _Optional[_Union[_User_pb2.User, _Mapping]] = ..., voice_info: _Optional[_Iterable[_Union[_Voice_pb2.Voice, _Mapping]]] = ..., thread_type: _Optional[int] = ..., fid: _Optional[int] = ..., fname: _Optional[str] = ..., is_livepost: _Optional[int] = ..., first_post_id: _Optional[int] = ..., create_time: _Optional[int] = ..., post_id: _Optional[int] = ..., author_id: _Optional[int] = ..., valid_post_num: _Optional[int] = ..., is_ad: _Optional[int] = ..., poll_info: _Optional[_Union[_PollInfo_pb2.PollInfo, _Mapping]] = ..., video_info: _Optional[_Union[_VideoInfo_pb2.VideoInfo, _Mapping]] = ..., agree: _Optional[_Union[_Agree_pb2.Agree, _Mapping]] = ..., share_num: _Optional[int] = ..., origin_thread_info: _Optional[_Union[ThreadInfo.OriginThreadInfo, _Mapping]] = ..., first_post_content: _Optional[_Iterable[_Union[_PbContent_pb2.PbContent, _Mapping]]] = ..., is_share_thread: _Optional[int] = ..., tab_id: _Optional[int] = ..., is_deleted: _Optional[int] = ..., collect_num: _Optional[int] = ..., is_frs_mask: _Optional[int] = ...) -> None: ...
