import itertools
from typing import List, Optional

from .._classdef import TypeMessage


class UserInfo_bawu(object):
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

    __slots__ = [
        '_user_id',
        '_portrait',
        '_user_name',
        '_nick_name_new',
        '_level',
    ]

    def __init__(self, data_proto: TypeMessage) -> None:
        self._user_id = data_proto.user_id
        self._portrait = data_proto.portrait
        self._user_name = data_proto.user_name
        self._nick_name_new = data_proto.name_show
        self._level = data_proto.user_level

    def __str__(self) -> str:
        return self._user_name or self._portrait or str(self._user_id)

    def __repr__(self) -> str:
        return str(
            {
                'user_id': self._user_id,
                'user_name': self._user_name,
                'portrait': self._portrait,
                'show_name': self.show_name,
                'level': self._level,
            }
        )

    def __eq__(self, obj: "UserInfo_bawu") -> bool:
        return self._user_id == obj._user_id

    def __hash__(self) -> int:
        return self._user_id

    def __int__(self) -> int:
        return self._user_id

    def __bool__(self) -> bool:
        return bool(self._user_id)

    @property
    def user_id(self) -> int:
        """
        用户user_id

        Note:
            唯一 不可变 不可为空
            请注意与用户个人页的tieba_uid区分
        """

        return self._user_id

    @property
    def portrait(self) -> str:
        """
        用户portrait

        Note:
            唯一 不可变 不可为空
        """

        return self._portrait

    @property
    def user_name(self) -> str:
        """
        用户名

        Note:
            唯一 可变 可为空
            请注意与用户昵称区分
        """

        return self._user_name

    @property
    def nick_name_new(self) -> str:
        """
        新版昵称
        """

        return self._nick_name_new

    @property
    def level(self) -> int:
        """
        等级
        """

        return self._level

    @property
    def nick_name(self) -> str:
        """
        用户昵称
        """

        return self._nick_name_new

    @property
    def show_name(self) -> str:
        """
        显示名称
        """

        return self._nick_name_new or self._user_name

    @property
    def log_name(self) -> str:
        """
        用于在日志中记录用户信息
        """

        if self._user_name:
            return self._user_name
        elif self._portrait:
            return f"{self._nick_name_new}/{self._portrait}"
        else:
            return str(self._user_id)


class BawuInfo(object):
    """
    吧务团队信息

    Attributes:
        all (list[UserInfo_bawu]): 所有吧务
        
        admin (list[UserInfo_bawu]): 大吧主
        profess_admin (list[UserInfo_bawu]): 职业吧主
        fourth_admin (list[UserInfo_bawu]): 第四吧主
        manager (list[UserInfo_bawu]): 小吧主
        video_editor (list[UserInfo_bawu]): 视频小编
        image_editor (list[UserInfo_bawu]): 图片小编
        voice_editor (list[UserInfo_bawu]): 语音小编
        broadcast_editor (list[UserInfo_bawu]): 广播小编
        journal_chief_editor (list[UserInfo_bawu]): 吧刊主编
        journal_editor (list[UserInfo_bawu]): 吧刊小编
    """
    
    __slots__ = [
        '_dict',
        '_list',
    ]

    keys = [
        '吧主',
        '职业吧主',
        '第四吧主',
        '小吧主',
        '视频小编',
        '图片小编',
        '语音小编',
        '广播小编',
        '吧刊主编',
        '吧刊小编',
    ]

    def __init__(self, data_proto: Optional[TypeMessage] = None) -> None:
        self._dict = dict.fromkeys(self.keys, [])
        self._list = None

        if data_proto:
            r_protos = data_proto.bawu_team_info.bawu_team_list
            self._dict.update(
                [r_proto.role_name, [UserInfo_bawu(p) for p in r_proto.role_info]] for r_proto in r_protos
            )

    @property
    def all(self) -> List[UserInfo_bawu]:
        """
        所有吧务
        """

        if self._list is None:
            self._list = list(itertools.chain.from_iterable(self._dict.values()))
        return self._list

    @property
    def admin(self) -> List[UserInfo_bawu]:
        """
        大吧主
        """

        return self._dict['吧主']

    @property
    def profess_admin(self) -> List[UserInfo_bawu]:
        """
        职业吧主
        """

        return self._dict['职业吧主']

    @property
    def fourth_admin(self) -> List[UserInfo_bawu]:
        """
        第四吧主
        """

        return self._dict['第四吧主']

    @property
    def manager(self) -> List[UserInfo_bawu]:
        """
        小吧主
        """

        return self._dict['小吧主']

    @property
    def video_editor(self) -> List[UserInfo_bawu]:
        """
        视频小编
        """

        return self._dict['视频小编']

    @property
    def image_editor(self) -> List[UserInfo_bawu]:
        """
        图片小编
        """

        return self._dict['图片小编']

    @property
    def voice_editor(self) -> List[UserInfo_bawu]:
        """
        语音小编
        """

        return self._dict['语音小编']

    @property
    def broadcast_editor(self) -> List[UserInfo_bawu]:
        """
        广播小编
        """

        return self._dict['广播小编']

    @property
    def journal_chief_editor(self) -> List[UserInfo_bawu]:
        """
        吧刊主编
        """

        return self._dict['吧刊主编']

    @property
    def journal_editor(self) -> List[UserInfo_bawu]:
        """
        吧刊小编
        """

        return self._dict['吧刊小编']
