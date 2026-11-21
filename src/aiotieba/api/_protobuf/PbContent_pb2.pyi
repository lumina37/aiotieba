from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class PbContent(_message.Message):
    __slots__ = ("type", "text", "link", "src", "bsize", "cdn_src", "big_cdn_src", "c", "voice_md5", "during_time", "uid", "width", "height", "origin_src", "origin_size", "count", "portrait", "tiebaplus_info", "item")
    class TiebaPlusInfo(_message.Message):
        __slots__ = ("title", "desc", "jump_url", "app_icon", "target_type", "h5_jump_type", "h5_jump_number", "h5_jump_param", "jump_type", "button_desc")
        TITLE_FIELD_NUMBER: _ClassVar[int]
        DESC_FIELD_NUMBER: _ClassVar[int]
        JUMP_URL_FIELD_NUMBER: _ClassVar[int]
        APP_ICON_FIELD_NUMBER: _ClassVar[int]
        TARGET_TYPE_FIELD_NUMBER: _ClassVar[int]
        H5_JUMP_TYPE_FIELD_NUMBER: _ClassVar[int]
        H5_JUMP_NUMBER_FIELD_NUMBER: _ClassVar[int]
        H5_JUMP_PARAM_FIELD_NUMBER: _ClassVar[int]
        JUMP_TYPE_FIELD_NUMBER: _ClassVar[int]
        BUTTON_DESC_FIELD_NUMBER: _ClassVar[int]
        title: str
        desc: str
        jump_url: str
        app_icon: str
        target_type: int
        h5_jump_type: int
        h5_jump_number: str
        h5_jump_param: str
        jump_type: int
        button_desc: str
        def __init__(self, title: _Optional[str] = ..., desc: _Optional[str] = ..., jump_url: _Optional[str] = ..., app_icon: _Optional[str] = ..., target_type: _Optional[int] = ..., h5_jump_type: _Optional[int] = ..., h5_jump_number: _Optional[str] = ..., h5_jump_param: _Optional[str] = ..., jump_type: _Optional[int] = ..., button_desc: _Optional[str] = ...) -> None: ...
    class Item(_message.Message):
        __slots__ = ("item_name",)
        ITEM_NAME_FIELD_NUMBER: _ClassVar[int]
        item_name: str
        def __init__(self, item_name: _Optional[str] = ...) -> None: ...
    TYPE_FIELD_NUMBER: _ClassVar[int]
    TEXT_FIELD_NUMBER: _ClassVar[int]
    LINK_FIELD_NUMBER: _ClassVar[int]
    SRC_FIELD_NUMBER: _ClassVar[int]
    BSIZE_FIELD_NUMBER: _ClassVar[int]
    CDN_SRC_FIELD_NUMBER: _ClassVar[int]
    BIG_CDN_SRC_FIELD_NUMBER: _ClassVar[int]
    C_FIELD_NUMBER: _ClassVar[int]
    VOICE_MD5_FIELD_NUMBER: _ClassVar[int]
    DURING_TIME_FIELD_NUMBER: _ClassVar[int]
    UID_FIELD_NUMBER: _ClassVar[int]
    WIDTH_FIELD_NUMBER: _ClassVar[int]
    HEIGHT_FIELD_NUMBER: _ClassVar[int]
    ORIGIN_SRC_FIELD_NUMBER: _ClassVar[int]
    ORIGIN_SIZE_FIELD_NUMBER: _ClassVar[int]
    COUNT_FIELD_NUMBER: _ClassVar[int]
    PORTRAIT_FIELD_NUMBER: _ClassVar[int]
    TIEBAPLUS_INFO_FIELD_NUMBER: _ClassVar[int]
    ITEM_FIELD_NUMBER: _ClassVar[int]
    type: int
    text: str
    link: str
    src: str
    bsize: str
    cdn_src: str
    big_cdn_src: str
    c: str
    voice_md5: str
    during_time: int
    uid: int
    width: int
    height: int
    origin_src: str
    origin_size: int
    count: int
    portrait: str
    tiebaplus_info: PbContent.TiebaPlusInfo
    item: PbContent.Item
    def __init__(self, type: _Optional[int] = ..., text: _Optional[str] = ..., link: _Optional[str] = ..., src: _Optional[str] = ..., bsize: _Optional[str] = ..., cdn_src: _Optional[str] = ..., big_cdn_src: _Optional[str] = ..., c: _Optional[str] = ..., voice_md5: _Optional[str] = ..., during_time: _Optional[int] = ..., uid: _Optional[int] = ..., width: _Optional[int] = ..., height: _Optional[int] = ..., origin_src: _Optional[str] = ..., origin_size: _Optional[int] = ..., count: _Optional[int] = ..., portrait: _Optional[str] = ..., tiebaplus_info: _Optional[_Union[PbContent.TiebaPlusInfo, _Mapping]] = ..., item: _Optional[_Union[PbContent.Item, _Mapping]] = ...) -> None: ...
