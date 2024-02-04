import dataclasses as dcs
from functools import cached_property
from typing import Protocol, TypeVar

import yarl

from .common import TypeMessage

TypeFragment = TypeVar('TypeFragment')


@dcs.dataclass
class FragText:
    """
    纯文本碎片

    Attributes:
        text (str): 文本内容
    """

    text: str = ""

    @staticmethod
    def from_tbdata(data_proto: TypeMessage) -> "FragText":
        text = data_proto.text
        return FragText(text)


class TypeFragText(Protocol):
    text: str


@dcs.dataclass
class FragEmoji:
    """
    表情碎片

    Attributes:
        id (str): 表情图片id
        desc (str): 表情描述
    """

    id: str = ""
    desc: str = ""

    @staticmethod
    def from_tbdata(data_proto: TypeMessage) -> "FragEmoji":
        id = data_proto.text
        desc = data_proto.c
        return FragEmoji(id, desc)


class TypeFragEmoji(Protocol):
    id: str
    desc: str


@dcs.dataclass
class FragImage:
    """
    图像碎片

    Attributes:
        src (str): 小图链接 宽720px
        big_src (str): 大图链接 宽960px
        origin_src (str): 原图链接
        origin_size (int): 原图大小
        show_width (int): 图像在客户端预览显示的宽度
        show_height (int): 图像在客户端预览显示的高度
        hash (str): 百度图床hash
    """

    src: str = ""
    big_src: str = ""
    origin_src: str = ""
    origin_size: int = 0
    show_width: int = 0
    show_height: int = 0

    @staticmethod
    def from_tbdata(data_proto: TypeMessage) -> "FragImage":
        src = data_proto.cdn_src
        big_src = data_proto.big_cdn_src
        origin_src = data_proto.origin_src
        origin_size = data_proto.origin_size

        show_width, _, show_height = data_proto.bsize.partition(',')
        show_width = int(show_width)
        show_height = int(show_height)

        return FragImage(src, big_src, origin_src, origin_size, show_width, show_height)

    @cached_property
    def hash(self) -> str:
        if self._hash is None:
            first_qmark_idx = self.src.find('?')
            end_idx = self.src.rfind('.', 0, first_qmark_idx)

            if end_idx == -1:
                self._hash = ''
            else:
                start_idx = self.src.rfind('/', 0, end_idx)
                self._hash = self.src[start_idx + 1 : end_idx]

        return self._hash


class TypeFragImage(Protocol):
    src: str = ""
    origin_src: str = ""

    @property
    def hash(self) -> str:
        ...


@dcs.dataclass
class FragAt:
    """
    @碎片

    Attributes:
        text (str): 被@用户的昵称 含@
        user_id (int): 被@用户的user_id
    """

    text: str = ""
    user_id: int = 0

    @staticmethod
    def from_tbdata(data_proto: TypeMessage) -> "FragAt":
        text = data_proto.text
        user_id = data_proto.uid
        return FragAt(text, user_id)


class TypeFragAt(Protocol):
    text: str
    user_id: int


@dcs.dataclass
class FragVoice:
    """
    音频碎片

    Attributes:
        md5 (str): 音频md5
        duration (int): 音频长度 以秒为单位
    """

    md5: str = ""
    duration: int = 0

    @staticmethod
    def from_tbdata(data_proto: TypeMessage) -> "FragVoice":
        voice_md5 = data_proto.voice_md5
        md5 = voice_md5[: voice_md5.rfind('_')]
        duration = data_proto.during_time / 1000
        return FragVoice(md5, duration)

    def __bool__(self) -> bool:
        return bool(self.md5)


class TypeFragVoice(Protocol):
    md5: str
    duration: int


@dcs.dataclass
class FragVideo:
    """
    视频碎片

    Attributes:
        src (str): 视频链接
        cover_src (str): 封面链接
        duration (int): 视频长度
        width (int): 视频宽度
        height (int): 视频高度
        view_num (int): 浏览次数
    """

    src: str = ""
    cover_src: str = ""
    duration: int = 0
    width: int = 0
    height: int = 0
    view_num: int = 0

    @staticmethod
    def from_tbdata(data_proto: TypeMessage) -> "FragVideo":
        src = data_proto.video_url
        cover_src = data_proto.thumbnail_url
        duration = data_proto.video_duration
        width = data_proto.video_width
        height = data_proto.video_height
        view_num = data_proto.play_count
        return FragVideo(src, cover_src, duration, width, height, view_num)

    def __bool__(self) -> bool:
        return bool(self.width)


class TypeFragVideo(Protocol):
    src: str
    cover_src: str
    duration: int
    width: int
    height: int
    view_num: int


@dcs.dataclass
class FragLink:
    """
    链接碎片

    Attributes:
        text (str): 原链接
        title (str): 链接标题
        raw_url (yarl.URL): 解析后的原链接
        url (yarl.URL): 解析后的去前缀链接
        is_external (bool): 是否外部链接
    """

    text: str = ""
    title: str = ""
    raw_url: yarl.URL = dcs.field(default_factory=yarl.URL)

    @staticmethod
    def from_tbdata(data_proto: TypeMessage) -> "FragLink":
        text = data_proto.link
        title = data_proto.text
        raw_url = yarl.URL(text)
        return FragLink(text, title, raw_url)

    @cached_property
    def url(self) -> yarl.URL:
        if self.is_external:
            url = yarl.URL(self.raw_url.query['url'])
        else:
            url = self.raw_url
        return url

    @cached_property
    def is_external(self) -> bool:
        return self.raw_url.path == "/mo/q/checkurl"


class TypeFragLink(Protocol):
    text: str
    title: str
    raw_url: yarl.URL

    @property
    def url(self) -> yarl.URL:
        ...

    @property
    def is_external(self) -> bool:
        ...


@dcs.dataclass
class FragTiebaPlus:
    """
    贴吧plus广告碎片

    Attributes:
        text (str): 贴吧plus广告描述
        url (yarl.URL): 解析后的贴吧plus广告跳转链接
    """

    text: str = ""
    url: yarl.URL = dcs.field(default_factory=yarl.URL)

    @staticmethod
    def from_tbdata(data_proto: TypeMessage) -> "FragTiebaPlus":
        text = data_proto.tiebaplus_info.desc
        url = yarl.URL(data_proto.tiebaplus_info.jump_url)
        return FragTiebaPlus(text, url)


class TypeFragTiebaPlus(Protocol):
    text: str
    url: yarl.URL


@dcs.dataclass
class FragItem:
    """
    item碎片

    Attributes:
        text (str): item名称
    """

    text: str = ""

    @staticmethod
    def from_tbdata(data_proto: TypeMessage) -> "FragItem":
        text = data_proto.item.item_name
        return FragItem(text)


class TypeFragItem(Protocol):
    text: str
