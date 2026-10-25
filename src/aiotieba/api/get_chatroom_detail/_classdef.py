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
        name (str): 用户名
        name_show (str): 显示名称
        portrait (str): 头像
        uk (str): baidu_uk
        user_id (int): 用户id
        robot_role (int): 机器人角色
        skills (list[RobotSkill]): 技能列表
    """

    name: str = ""
    name_show: str = ""
    portrait: str = ""
    uk: str = ""
    user_id: int = 0
    robot_role: int = 0
    skills: list[RobotSkill] = dcs.field(default_factory=list)

    @classmethod
    def from_json(cls, data_map: Mapping) -> Self:
        user_map = data_map["user"]

        name = user_map["name"]
        name_show = user_map["name_show"]
        portrait = user_map["portrait"]
        uk = user_map["uk"]
        user_id = bduk2user_id(uk)
        robot_role = int(user_map["robot_role"])
        skills = [RobotSkill.from_json(x) for x in data_map["skill"]]

        return cls(name, name_show, portrait, uk, user_id, robot_role, skills)


@dcs.dataclass
class ChatroomDetail(TbErrorExt):
    """
    吧群聊天室详情

    Attributes:
        err (Exception | None): 捕获的异常

        room_id (int): 聊天室id
        forum_id (int): 吧id
        forum_name (str): 吧名
        name (str): 群名
        avatar (str): 群头像
        discuss_num (int): 群成员数
        announce (str): 群公告
        talk_threshold_level (int): 发言等级门槛
        is_talk_banned (bool): 是否被禁言
        robots (list[Robot]): 机器人列表
    """

    room_id: int = 0
    forum_id: int = 0
    forum_name: str = ""
    name: str = ""
    avatar: str = ""
    discuss_num: int = 0
    announce: str = ""
    talk_threshold_level: int = 0
    is_talk_banned: bool = False
    robots: list[Robot] = dcs.field(default_factory=list)

    @classmethod
    def from_json(cls, data_map: Mapping) -> Self:
        basic_info = data_map["basic_info"]
        extra_info = data_map["extra_info"]
        bots = data_map["bots"]

        room_id = int(basic_info["id"])
        forum_id = int(basic_info["forum_id"])
        forum_name = basic_info["forum_name"]
        name = basic_info["name"]
        avatar = basic_info["avatar"]
        discuss_num = int(basic_info["discuss_num"])
        announce = extra_info["announce"]
        talk_threshold_level = int(extra_info["talk_threshold_level"])
        is_talk_banned = bool(int(extra_info["is_talk_banned"]))
        robots = [Robot.from_json(x) for x in bots["bot_list"]]

        return cls(
            room_id,
            forum_id,
            forum_name,
            name,
            avatar,
            discuss_num,
            announce,
            talk_threshold_level,
            is_talk_banned,
            robots,
        )
