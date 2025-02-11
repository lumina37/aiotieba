from __future__ import annotations

import dataclasses as dcs
from functools import cached_property
from typing import TYPE_CHECKING

from ...exception import TbErrorExt
from .._classdef import Containers
from .._classdef.contents import _IMAGEHASH_EXP, TypeFragment, TypeFragText

if TYPE_CHECKING:
    from collections.abc import Mapping


@dcs.dataclass
class FragText_ri:
    """
    纯文本碎片

    Attributes:
        text (str): 文本内容
    """

    text: str = ""

    @staticmethod
    def from_tbdata(data_map: Mapping) -> FragText_ri:
        text = data_map["value"]
        return FragText_ri(text)


@dcs.dataclass
class FragImage_ri:
    """
    图像碎片

    Attributes:
        src (str): 小图链接 宽720px
        show_width (int): 图像在客户端预览显示的宽度
        show_height (int): 图像在客户端预览显示的高度
        hash (str): 百度图床hash
    """

    src: str = dcs.field(default="", repr=False)
    show_width: int = 0
    show_height: int = 0
    hash: str = ""

    @staticmethod
    def from_tbdata(data_map: Mapping) -> FragImage_ri:
        src = data_map["url"]
        show_width = int(data_map["width"])
        show_height = int(data_map["height"])

        hash_ = _IMAGEHASH_EXP.search(src).group(1)

        return FragImage_ri(src, show_width, show_height, hash_)


@dcs.dataclass
class Contents_ri(Containers[TypeFragment]):
    """
    内容碎片列表

    Attributes:
        objs (list[TypeFragment]): 所有内容碎片的混合列表

        text (str): 文本内容

        texts (list[TypeFragText]): 纯文本碎片列表
        imgs (list[FragImage_t]): 图像碎片列表
    """

    texts: list[TypeFragText] = dcs.field(default_factory=list, repr=False)
    imgs: list[FragImage_ri] = dcs.field(default_factory=list, repr=False)

    @staticmethod
    def from_tbdata(data_map: Mapping) -> Contents_ri:
        content_maps = data_map["content_detail"]

        texts = []
        imgs = [FragImage_ri.from_tbdata(m) for m in data_map["all_pics"]]

        def _frags():
            for cmap in content_maps:
                _type = cmap["type"]
                # 1纯文本
                if _type == 1:
                    frag = FragText_ri.from_tbdata(cmap)
                    texts.append(frag)
                    yield frag
                elif _type == 3:
                    continue
                else:
                    from ...logging import get_logger as LOG

                    LOG().warning("Unknown fragment type. type=%s proto=%s", _type, cmap)

        objs = list(_frags())
        objs += imgs

        return Contents_ri(objs, texts, imgs)

    @cached_property
    def text(self) -> str:
        text = "".join(frag.text for frag in self.texts)
        return text


@dcs.dataclass
class UserInfo_ri:
    """
    用户信息

    Attributes:
        portrait (str): portrait
        user_name (str): 用户名
        nick_name_new (str): 新版昵称

        nick_name (str): 用户昵称
        show_name (str): 显示名称
        log_name (str): 用于在日志中记录用户信息
    """

    portrait: str = ""
    user_name: str = ""
    nick_name_new: str = ""

    @staticmethod
    def from_tbdata(data_map: Mapping) -> UserInfo_ri:
        portrait = data_map["portrait"]
        if "?" in portrait:
            portrait = portrait[:-13]
        user_name = data_map["user_name"]
        nick_name_new = data_map["show_nickname"]
        return UserInfo_ri(portrait, user_name, nick_name_new)

    def __str__(self) -> str:
        return self.user_name or self.portrait

    def __eq__(self, obj: UserInfo_ri) -> bool:
        return self.portrait == obj.portrait

    def __hash__(self) -> int:
        return hash(self.portrait)

    def __bool__(self) -> bool:
        return bool(self.portrait)

    @property
    def nick_name(self) -> str:
        return self.nick_name_new

    @property
    def show_name(self) -> str:
        return self.nick_name_new or self.user_name

    @cached_property
    def log_name(self) -> str:
        return self.user_name or f"{self.nick_name_new}/{self.portrait}"


@dcs.dataclass
class RecoverInfo(TbErrorExt):
    """
    待恢复帖子信息

    Attributes:
        text (str): 文本内容
        contents (Contents_ri): 正文内容碎片列表
        title (str): 标题内容

        tid (int): 所在主题帖id
        pid (int): 回复id
        user (UserInfo_ri): 发布者的用户信息
    """

    contents: Contents_ri = dcs.field(default_factory=Contents_ri)
    title: str = ""

    tid: int = 0
    pid: int = 0
    user: UserInfo_ri = dcs.field(default_factory=UserInfo_ri)

    @staticmethod
    def from_tbdata(data_map: Mapping) -> RecoverInfo:
        thread_info = data_map["thread_info"]

        contents = Contents_ri.from_tbdata(thread_info)
        title = thread_info["title"]

        tid = thread_info["thread_id"]
        pid = thread_info["post_id"]
        user = UserInfo_ri.from_tbdata(data_map["user_info"])

        return RecoverInfo(contents, title, tid, pid, user)

    def __eq__(self, obj: RecoverInfo) -> bool:
        return self.pid == obj.pid

    def __hash__(self) -> int:
        return self.pid

    @cached_property
    def text(self) -> str:
        if self.title:
            text = f"{self.title}\n{self.contents.text}"
        else:
            text = self.contents.text
        return text
