from __future__ import annotations

import dataclasses as dcs
from typing import TYPE_CHECKING, Self

from ...exception import TbErrorExt
from ...helper.crypto import bduk2user_id

if TYPE_CHECKING:
    from collections.abc import Mapping


@dcs.dataclass
class RobotSkill:
    """
    吧群机器人的技能

    Attributes:
        type (int): 技能类型
        name (str): 技能名称
        alias (str): 技能别名
        desc (str): 技能描述
        is_show (bool): 是否展示
        items (list[dict]): 技能参数列表
    """

    type: int = 0
    name: str = ""
    alias: str = ""
    desc: str = ""
    is_show: bool = False
    items: list[dict] = dcs.field(default_factory=list)

    @classmethod
    def from_json(cls, data_map: Mapping) -> Self:
        skill_type = int(data_map["type"])
        name = data_map["name"]
        alias = data_map["alias"]
        desc = data_map["desc"]
        is_show = bool(int(data_map["is_show"]))
        items = data_map["items"]

        return cls(skill_type, name, alias, desc, is_show, items)


@dcs.dataclass
class Robot:
    """
    吧群机器人

    Attributes:
        user_id (int): 用户id
        portrait (str): 头像
        user_name (str): 用户名
        name_show (str): 显示名称
        bduk (str): baidu_uk

        robot_role (int): 机器人角色
        skills (list[RobotSkill]): 技能列表
    """

    user_id: int = 0
    portrait: str = ""
    user_name: str = ""
    name_show: str = ""
    bduk: str = ""

    robot_role: int = 0
    skills: list[RobotSkill] = dcs.field(default_factory=list)

    @classmethod
    def from_json(cls, data_map: Mapping) -> Self:
        user_map = data_map["user"]

        bduk = user_map["uk"]
        user_id = bduk2user_id(bduk)
        portrait = user_map["portrait"]
        user_name = user_map["name"]
        name_show = user_map["name_show"]
        robot_role = int(user_map["robot_role"])
        skills = [RobotSkill.from_json(x) for x in data_map["skill"]]

        return cls(user_id, portrait, user_name, name_show, bduk, robot_role, skills)


@dcs.dataclass
class ChatroomDetail(TbErrorExt):
    """
    吧群聊天室详情

    Attributes:
        err (Exception | None): 捕获的异常

        fid (int): 吧id
        fname (str): 吧名
        room_id (int): 聊天室id

        name (str): 群名
        avatar (str): 群头像
        announce (str): 群公告
        member_num (int): 群成员数

        chat_threshold (int): 发言等级门槛
        robots (list[Robot]): 机器人列表
    """

    fid: int = 0
    fname: str = ""
    room_id: int = 0

    name: str = ""
    avatar: str = ""
    announce: str = ""
    member_num: int = 0

    chat_threshold: int = 0
    robots: list[Robot] = dcs.field(default_factory=list)

    @classmethod
    def from_json(cls, data_map: Mapping) -> Self:
        basic_info = data_map["basic_info"]
        extra_info = data_map["extra_info"]
        bots = data_map["bots"]

        fid = int(basic_info["forum_id"])
        fname = basic_info["forum_name"]
        room_id = int(basic_info["id"])

        name = basic_info["name"]
        avatar = basic_info["avatar"]
        announce = extra_info["announce"]
        member_num = int(basic_info["discuss_num"])

        chat_threshold = int(extra_info["talk_threshold_level"])
        robots = [Robot.from_json(x) for x in bots["bot_list"]]

        return cls(fid, fname, room_id, name, avatar, announce, member_num, chat_threshold, robots)
