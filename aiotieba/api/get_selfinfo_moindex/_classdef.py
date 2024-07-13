from __future__ import annotations

import dataclasses as dcs
from functools import cached_property
from typing import Mapping

from ...enums import Gender


@dcs.dataclass
class UserInfo_moindex:
    """
    用户信息

    Attributes:
        user_id (int): user_id
        portrait (str): portrait
        user_name (str): 用户名

        gender (Gender): 性别
        post_num (int): 发帖数
        fan_num (int): 粉丝数
        follow_num (int): 关注数
        forum_num (int): 关注贴吧数
        sign (str): 个性签名

        is_vip (bool): 是否超级会员

        log_name (str): 用于在日志中记录用户信息
    """

    user_id: int = 0
    portrait: str = ''
    user_name: str = ''

    gender: Gender = Gender.UNKNOWN
    post_num: int = 0
    fan_num: int = 0
    follow_num: int = 0
    forum_num: int = 0
    sign: str = ""

    is_vip: bool = False

    @staticmethod
    def from_tbdata(data_map: Mapping) -> UserInfo_moindex:
        user_id = data_map['id']
        portrait = data_map['portrait']
        user_name = data_map['name']

        gender = Gender(data_map['user_sex'])
        post_num = data_map['post_num']
        fan_num = data_map['fans_num']
        follow_num = data_map['concern_num']
        forum_num = data_map['like_forum_num']
        sign = data_map['intro']

        if vip_dict := data_map['vipInfo']:
            is_vip = int(vip_dict['v_status']) == 3
        else:
            is_vip = False

        return UserInfo_moindex(
            user_id, portrait, user_name, gender, post_num, fan_num, follow_num, forum_num, sign, is_vip
        )

    def __str__(self) -> str:
        return self.user_name or self.portrait

    def __eq__(self, obj: UserInfo_moindex) -> bool:
        return self.user_id == obj.user_id

    def __hash__(self) -> int:
        return self.user_id

    def __bool__(self) -> bool:
        return self.user_id

    @cached_property
    def log_name(self) -> str:
        return self.user_name or self.portrait
