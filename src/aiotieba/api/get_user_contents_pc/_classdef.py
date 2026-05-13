from __future__ import annotations

import dataclasses as dcs
from functools import cached_property
from typing import TYPE_CHECKING

from .._classdef import Containers
from .._classdef.contents import (
    FragAt,
    FragEmoji,
    FragLink,
    FragText,
    FragUnknown,
    FragVideo,
    FragVoice,
    TypeFragment,
    TypeFragText,
)

if TYPE_CHECKING:
    from collections.abc import Mapping


FragText_up = FragText_ut = FragText
FragEmoji_ut = FragEmoji
FragAt_ut = FragAt
FragLink_up = FragLink_ut = FragLink
FragVideo_ut = FragVideo
FragVoice_ut = FragVoice


@dcs.dataclass
class FragVoice_up:
    """
    音频碎片

    Attributes:
        md5 (str): 音频md5
        duration (float): 音频长度 以秒为单位
    """

    md5: str = ""
    duration: float = 0.0

    @staticmethod
    def from_json(data_map: Mapping) -> FragVoice_up:
        md5 = data_map["voice_md5"]
        duration = int(data_map["during_time"]) / 1000
        return FragVoice_up(md5, duration)

    def __bool__(self) -> bool:
        return bool(self.md5)


@dcs.dataclass
class Contents_pcup(Containers[TypeFragment]):
    """
    内容碎片列表

    Attributes:
        objs (list[TypeFragment]): 所有内容碎片的混合列表

        text (str): 文本内容

        texts (list[TypeFragText]): 纯文本碎片列表
        links (list[FragLink_up]): 链接碎片列表
        voice (FragVoice_up): 音频碎片
    """

    texts: list[TypeFragText] = dcs.field(default_factory=list, repr=False)
    links: list[FragLink_up] = dcs.field(default_factory=list, repr=False)
    voice: FragVoice_up = dcs.field(default_factory=FragVoice_up, repr=False)

    @staticmethod
    def from_json(data_map: Mapping) -> Contents_pcup:
        content_maps = data_map["content"]

        texts = []
        links = []
        voice = FragVoice_up()

        def _frags():
            for content_map in content_maps:
                _type = int(content_map["type"])
                if _type in [0, 4]:
                    frag = FragText_up.from_json(content_map)
                    texts.append(frag)
                    yield frag
                elif _type == 1:
                    frag = FragLink_up.from_json(content_map)
                    links.append(frag)
                    texts.append(frag)
                    yield frag
                elif _type == 10:  # voice
                    nonlocal voice
                    voice = FragVoice_up.from_json(content_map)
                    continue
                else:
                    yield FragUnknown.from_json(content_map)

        objs = list(_frags())

        return Contents_pcup(objs, texts, links, voice)

    @cached_property
    def text(self) -> str:
        text = "".join(frag.text for frag in self.texts)
        return text


@dcs.dataclass
class UserInfo_pcu:
    """
    用户信息

    Attributes:
        user_id (int): user_id
        portrait (str): portrait
        user_name (str): 用户名
        nick_name_new (str): 新版昵称

        nick_name (str): 用户昵称
        show_name (str): 显示名称
        log_name (str): 用于在日志中记录用户信息
    """

    user_id: int = 0
    portrait: str = ""
    user_name: str = ""
    nick_name_new: str = ""

    @staticmethod
    def from_json(data_map: Mapping) -> UserInfo_pcu:
        user_id = data_map["id"]
        portrait = data_map["portrait"]
        if "?" in portrait:
            portrait = portrait[:-13]
        user_name = data_map["name"]
        nick_name_new = data_map["name_show"]
        return UserInfo_pcu(user_id, portrait, user_name, nick_name_new)

    def __str__(self) -> str:
        return self.user_name or self.portrait or str(self.user_id)

    def __eq__(self, obj: UserInfo_pcu) -> bool:
        return self.user_id == obj.user_id

    def __hash__(self) -> int:
        return self.user_id

    def __bool__(self) -> bool:
        return bool(self.user_id)

    @property
    def nick_name(self) -> str:
        return self.nick_name_new

    @property
    def show_name(self) -> str:
        return self.nick_name_new or self.user_name

    @cached_property
    def log_name(self) -> str:
        if self.user_name:
            return self.user_name
        elif self.portrait:
            return f"{self.nick_name_new}/{self.portrait}"
        else:
            return str(self.user_id)


@dcs.dataclass
class PcUserPost:
    """
    用户历史回复信息

    Attributes:
        text (str): 文本内容
        contents (Contents_pcup): 正文内容碎片列表

        fid (int): 所在吧id
        tid (int): 所在主题帖id
        pid (int): 回复id
        user (UserInfo_pcu): 发布者的用户信息
        author_id (int): 发布者的user_id

        create_time (int): 创建时间 10位时间戳 以秒为单位
    """

    contents: Contents_pcup = dcs.field(default_factory=Contents_pcup)

    fid: int = 0
    tid: int = 0
    pid: int = 0
    user: UserInfo_pcu = dcs.field(default_factory=UserInfo_pcu)

    create_time: int = 0

    @staticmethod
    def from_json(data_map: Mapping) -> PcUserPost:
        post_info = data_map["post_info"]
        contents = Contents_pcup.from_json(post_info)
        pid = post_info["id"]
        create_time = post_info["time"]
        return PcUserPost(contents, 0, 0, pid, None, create_time)

    def __eq__(self, obj: PcUserPost) -> bool:
        return self.pid == obj.pid

    def __hash__(self) -> int:
        return self.pid

    @property
    def text(self) -> str:
        return self.contents.text

    @property
    def author_id(self) -> int:
        return self.user.user_id


@dcs.dataclass
class PcUserPosts(Containers[PcUserPost]):
    """
    用户历史回复信息列表

    Attributes:
        objs (list[PcUserPost]): 用户历史回复信息列表
    """

    @staticmethod
    def from_json(data_map: Mapping) -> PcUserPosts:
        user = UserInfo_pcu.from_json(data_map["list"][0]["post_info"]["author"])
        objs = [PcUserPost.from_json(m) for m in data_map["list"]]
        for upost in objs:
            upost.user = user

        return PcUserPosts(objs)
