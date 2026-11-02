from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class User(_message.Message):
    __slots__ = ("id", "name", "name_show", "portrait", "iconinfo", "is_coreuser", "level_id", "is_bawu", "bawu_type", "BDUSS", "fans_num", "concern_num", "sex", "my_like_num", "intro", "post_num", "tb_age", "is_mem", "gender", "priv_sets", "is_friend", "likeForum", "is_guanfang", "thread_num", "is_fans", "is_default_avatar", "tieba_uid", "ip_address", "user_growth")
    class Icon(_message.Message):
        __slots__ = ("name",)
        NAME_FIELD_NUMBER: _ClassVar[int]
        name: str
        def __init__(self, name: _Optional[str] = ...) -> None: ...
    class PrivSets(_message.Message):
        __slots__ = ("location", "like", "group", "post", "friend", "live", "reply", "bazhu_show_inside", "bazhu_show_outside")
        LOCATION_FIELD_NUMBER: _ClassVar[int]
        LIKE_FIELD_NUMBER: _ClassVar[int]
        GROUP_FIELD_NUMBER: _ClassVar[int]
        POST_FIELD_NUMBER: _ClassVar[int]
        FRIEND_FIELD_NUMBER: _ClassVar[int]
        LIVE_FIELD_NUMBER: _ClassVar[int]
        REPLY_FIELD_NUMBER: _ClassVar[int]
        BAZHU_SHOW_INSIDE_FIELD_NUMBER: _ClassVar[int]
        BAZHU_SHOW_OUTSIDE_FIELD_NUMBER: _ClassVar[int]
        location: int
        like: int
        group: int
        post: int
        friend: int
        live: int
        reply: int
        bazhu_show_inside: int
        bazhu_show_outside: int
        def __init__(self, location: _Optional[int] = ..., like: _Optional[int] = ..., group: _Optional[int] = ..., post: _Optional[int] = ..., friend: _Optional[int] = ..., live: _Optional[int] = ..., reply: _Optional[int] = ..., bazhu_show_inside: _Optional[int] = ..., bazhu_show_outside: _Optional[int] = ...) -> None: ...
    class LikeForumInfo(_message.Message):
        __slots__ = ("forum_name", "forum_id")
        FORUM_NAME_FIELD_NUMBER: _ClassVar[int]
        FORUM_ID_FIELD_NUMBER: _ClassVar[int]
        forum_name: str
        forum_id: int
        def __init__(self, forum_name: _Optional[str] = ..., forum_id: _Optional[int] = ...) -> None: ...
    class UserGrowth(_message.Message):
        __slots__ = ("level_id",)
        LEVEL_ID_FIELD_NUMBER: _ClassVar[int]
        level_id: int
        def __init__(self, level_id: _Optional[int] = ...) -> None: ...
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    NAME_SHOW_FIELD_NUMBER: _ClassVar[int]
    PORTRAIT_FIELD_NUMBER: _ClassVar[int]
    ICONINFO_FIELD_NUMBER: _ClassVar[int]
    IS_COREUSER_FIELD_NUMBER: _ClassVar[int]
    LEVEL_ID_FIELD_NUMBER: _ClassVar[int]
    IS_BAWU_FIELD_NUMBER: _ClassVar[int]
    BAWU_TYPE_FIELD_NUMBER: _ClassVar[int]
    BDUSS_FIELD_NUMBER: _ClassVar[int]
    FANS_NUM_FIELD_NUMBER: _ClassVar[int]
    CONCERN_NUM_FIELD_NUMBER: _ClassVar[int]
    SEX_FIELD_NUMBER: _ClassVar[int]
    MY_LIKE_NUM_FIELD_NUMBER: _ClassVar[int]
    INTRO_FIELD_NUMBER: _ClassVar[int]
    POST_NUM_FIELD_NUMBER: _ClassVar[int]
    TB_AGE_FIELD_NUMBER: _ClassVar[int]
    IS_MEM_FIELD_NUMBER: _ClassVar[int]
    GENDER_FIELD_NUMBER: _ClassVar[int]
    PRIV_SETS_FIELD_NUMBER: _ClassVar[int]
    IS_FRIEND_FIELD_NUMBER: _ClassVar[int]
    LIKEFORUM_FIELD_NUMBER: _ClassVar[int]
    IS_GUANFANG_FIELD_NUMBER: _ClassVar[int]
    THREAD_NUM_FIELD_NUMBER: _ClassVar[int]
    IS_FANS_FIELD_NUMBER: _ClassVar[int]
    IS_DEFAULT_AVATAR_FIELD_NUMBER: _ClassVar[int]
    TIEBA_UID_FIELD_NUMBER: _ClassVar[int]
    IP_ADDRESS_FIELD_NUMBER: _ClassVar[int]
    USER_GROWTH_FIELD_NUMBER: _ClassVar[int]
    id: int
    name: str
    name_show: str
    portrait: str
    iconinfo: _containers.RepeatedCompositeFieldContainer[User.Icon]
    is_coreuser: int
    level_id: int
    is_bawu: int
    bawu_type: str
    BDUSS: str
    fans_num: int
    concern_num: int
    sex: int
    my_like_num: int
    intro: str
    post_num: int
    tb_age: str
    is_mem: int
    gender: int
    priv_sets: User.PrivSets
    is_friend: int
    likeForum: _containers.RepeatedCompositeFieldContainer[User.LikeForumInfo]
    is_guanfang: int
    thread_num: int
    is_fans: int
    is_default_avatar: int
    tieba_uid: str
    ip_address: str
    user_growth: User.UserGrowth
    def __init__(self, id: _Optional[int] = ..., name: _Optional[str] = ..., name_show: _Optional[str] = ..., portrait: _Optional[str] = ..., iconinfo: _Optional[_Iterable[_Union[User.Icon, _Mapping]]] = ..., is_coreuser: _Optional[int] = ..., level_id: _Optional[int] = ..., is_bawu: _Optional[int] = ..., bawu_type: _Optional[str] = ..., BDUSS: _Optional[str] = ..., fans_num: _Optional[int] = ..., concern_num: _Optional[int] = ..., sex: _Optional[int] = ..., my_like_num: _Optional[int] = ..., intro: _Optional[str] = ..., post_num: _Optional[int] = ..., tb_age: _Optional[str] = ..., is_mem: _Optional[int] = ..., gender: _Optional[int] = ..., priv_sets: _Optional[_Union[User.PrivSets, _Mapping]] = ..., is_friend: _Optional[int] = ..., likeForum: _Optional[_Iterable[_Union[User.LikeForumInfo, _Mapping]]] = ..., is_guanfang: _Optional[int] = ..., thread_num: _Optional[int] = ..., is_fans: _Optional[int] = ..., is_default_avatar: _Optional[int] = ..., tieba_uid: _Optional[str] = ..., ip_address: _Optional[str] = ..., user_growth: _Optional[_Union[User.UserGrowth, _Mapping]] = ...) -> None: ...
