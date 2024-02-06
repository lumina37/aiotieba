import dataclasses as dcs
from functools import cached_property
from typing import List

from .._classdef import TypeMessage


@dcs.dataclass
class UserInfo_bawu:
    """
    用户信息

    Attributes:
        user_id (int): user_id
        portrait (str): portrait
        user_name (str): 用户名
        nick_name_new (str): 新版昵称

        level (int): 等级

        nick_name (str): 用户昵称
        show_name (str): 显示名称
        log_name (str): 用于在日志中记录用户信息
    """

    user_id: int = 0
    portrait: str = ''
    user_name: str = ''
    nick_name_new: str = ''

    level: int = 0

    @staticmethod
    def from_tbdata(data_proto: TypeMessage) -> "UserInfo_bawu":
        user_id = data_proto.user_id
        portrait = data_proto.portrait
        user_name = data_proto.user_name
        nick_name_new = data_proto.name_show
        level = data_proto.user_level
        return UserInfo_bawu(user_id, portrait, user_name, nick_name_new, level)

    def __str__(self) -> str:
        return self.user_name or self.portrait or str(self.user_id)

    def __eq__(self, obj: "UserInfo_bawu") -> bool:
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
class BawuInfo:
    """
    吧务团队信息

    Attributes:
        all (list[UserInfo_bawu]): 所有吧务

        admin (list[UserInfo_bawu]): 大吧主
        manager (list[UserInfo_bawu]): 小吧主
        voice_editor (list[UserInfo_bawu]): 语音小编
        image_editor (list[UserInfo_bawu]): 图片小编
        video_editor (list[UserInfo_bawu]): 视频小编
        broadcast_editor (list[UserInfo_bawu]): 广播小编
        journal_chief_editor (list[UserInfo_bawu]): 吧刊主编
        journal_editor (list[UserInfo_bawu]): 吧刊小编
        profess_admin (list[UserInfo_bawu]): 职业吧主
        fourth_admin (list[UserInfo_bawu]): 第四吧主
    """

    all: List[UserInfo_bawu] = dcs.field(default_factory=list, repr=False)

    admin: List[UserInfo_bawu] = dcs.field(default_factory=list)
    manager: List[UserInfo_bawu] = dcs.field(default_factory=list)
    voice_editor: List[UserInfo_bawu] = dcs.field(default_factory=list)
    image_editor: List[UserInfo_bawu] = dcs.field(default_factory=list)
    video_editor: List[UserInfo_bawu] = dcs.field(default_factory=list)
    broadcast_editor: List[UserInfo_bawu] = dcs.field(default_factory=list)
    journal_chief_editor: List[UserInfo_bawu] = dcs.field(default_factory=list)
    journal_editor: List[UserInfo_bawu] = dcs.field(default_factory=list)
    profess_admin: List[UserInfo_bawu] = dcs.field(default_factory=list)
    fourth_admin: List[UserInfo_bawu] = dcs.field(default_factory=list)

    @staticmethod
    def from_tbdata(data_proto: TypeMessage) -> "BawuInfo":
        all = []
        r_protos = data_proto.bawu_team_info.bawu_team_list
        _dict = {r_proto.role_name: [UserInfo_bawu.from_tbdata(p) for p in r_proto.role_info] for r_proto in r_protos}

        def extract(role_name: str) -> List[UserInfo_bawu]:
            if users := _dict.get(role_name):
                all.extend(users)
            else:
                users = []
            return users

        admin = extract('吧主')
        manager = extract('小吧主')
        voice_editor = extract('语音小编')
        image_editor = extract('图片小编')
        video_editor = extract('视频小编')
        broadcast_editor = extract('广播小编')
        journal_chief_editor = extract('吧刊主编')
        journal_editor = extract('吧刊小编')
        profess_admin = extract('职业吧主')
        fourth_admin = extract('第四吧主')

        return BawuInfo(
            all,
            admin,
            manager,
            voice_editor,
            image_editor,
            video_editor,
            broadcast_editor,
            journal_chief_editor,
            journal_editor,
            profess_admin,
            fourth_admin,
        )
