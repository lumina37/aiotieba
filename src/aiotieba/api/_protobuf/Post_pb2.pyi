from . import PbContent_pb2 as _PbContent_pb2
from . import SubPostList_pb2 as _SubPostList_pb2
from . import User_pb2 as _User_pb2
from . import Agree_pb2 as _Agree_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Post(_message.Message):
    __slots__ = ("id", "floor", "time", "content", "sub_post_number", "author_id", "sub_post_list", "signature", "author", "agree", "tid", "chat_content", "sprite_meme_info")
    class SubPost(_message.Message):
        __slots__ = ("sub_post_list",)
        SUB_POST_LIST_FIELD_NUMBER: _ClassVar[int]
        sub_post_list: _containers.RepeatedCompositeFieldContainer[_SubPostList_pb2.SubPostList]
        def __init__(self, sub_post_list: _Optional[_Iterable[_Union[_SubPostList_pb2.SubPostList, _Mapping]]] = ...) -> None: ...
    class SignatureData(_message.Message):
        __slots__ = ("content",)
        class SignatureContent(_message.Message):
            __slots__ = ("type", "text")
            TYPE_FIELD_NUMBER: _ClassVar[int]
            TEXT_FIELD_NUMBER: _ClassVar[int]
            type: int
            text: str
            def __init__(self, type: _Optional[int] = ..., text: _Optional[str] = ...) -> None: ...
        CONTENT_FIELD_NUMBER: _ClassVar[int]
        content: _containers.RepeatedCompositeFieldContainer[Post.SignatureData.SignatureContent]
        def __init__(self, content: _Optional[_Iterable[_Union[Post.SignatureData.SignatureContent, _Mapping]]] = ...) -> None: ...
    class ChatContent(_message.Message):
        __slots__ = ("bot_uk",)
        BOT_UK_FIELD_NUMBER: _ClassVar[int]
        bot_uk: str
        def __init__(self, bot_uk: _Optional[str] = ...) -> None: ...
    class SpriteMemeInfo(_message.Message):
        __slots__ = ("meme_id",)
        MEME_ID_FIELD_NUMBER: _ClassVar[int]
        meme_id: int
        def __init__(self, meme_id: _Optional[int] = ...) -> None: ...
    ID_FIELD_NUMBER: _ClassVar[int]
    FLOOR_FIELD_NUMBER: _ClassVar[int]
    TIME_FIELD_NUMBER: _ClassVar[int]
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    SUB_POST_NUMBER_FIELD_NUMBER: _ClassVar[int]
    AUTHOR_ID_FIELD_NUMBER: _ClassVar[int]
    SUB_POST_LIST_FIELD_NUMBER: _ClassVar[int]
    SIGNATURE_FIELD_NUMBER: _ClassVar[int]
    AUTHOR_FIELD_NUMBER: _ClassVar[int]
    AGREE_FIELD_NUMBER: _ClassVar[int]
    TID_FIELD_NUMBER: _ClassVar[int]
    CHAT_CONTENT_FIELD_NUMBER: _ClassVar[int]
    SPRITE_MEME_INFO_FIELD_NUMBER: _ClassVar[int]
    id: int
    floor: int
    time: int
    content: _containers.RepeatedCompositeFieldContainer[_PbContent_pb2.PbContent]
    sub_post_number: int
    author_id: int
    sub_post_list: Post.SubPost
    signature: Post.SignatureData
    author: _User_pb2.User
    agree: _Agree_pb2.Agree
    tid: int
    chat_content: Post.ChatContent
    sprite_meme_info: Post.SpriteMemeInfo
    def __init__(self, id: _Optional[int] = ..., floor: _Optional[int] = ..., time: _Optional[int] = ..., content: _Optional[_Iterable[_Union[_PbContent_pb2.PbContent, _Mapping]]] = ..., sub_post_number: _Optional[int] = ..., author_id: _Optional[int] = ..., sub_post_list: _Optional[_Union[Post.SubPost, _Mapping]] = ..., signature: _Optional[_Union[Post.SignatureData, _Mapping]] = ..., author: _Optional[_Union[_User_pb2.User, _Mapping]] = ..., agree: _Optional[_Union[_Agree_pb2.Agree, _Mapping]] = ..., tid: _Optional[int] = ..., chat_content: _Optional[_Union[Post.ChatContent, _Mapping]] = ..., sprite_meme_info: _Optional[_Union[Post.SpriteMemeInfo, _Mapping]] = ...) -> None: ...
