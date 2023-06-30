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
            唯一 不可变 不可为空\n
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
            唯一 可变 可为空\n
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

    __slots__ = [
        '_all',
        '_admin',
        '_manager',
        '_voice_editor',
        '_image_editor',
        '_video_editor',
        '_broadcast_editor',
        '_journal_chief_editor',
        '_journal_editor',
        '_profess_admin',
        '_fourth_admin',
    ]

    def __init__(self, data_proto: Optional[TypeMessage] = None) -> None:
        self._all = []
        if data_proto:
            r_protos = data_proto.bawu_team_info.bawu_team_list
            _dict = {r_proto.role_name: [UserInfo_bawu(p) for p in r_proto.role_info] for r_proto in r_protos}

            def extract(role_name: str) -> List[UserInfo_bawu]:
                if users := _dict.get(role_name):
                    self._all.extend(users)
                else:
                    users = []
                return users

            self._admin = extract('吧主')
            self._manager = extract('小吧主')
            self._voice_editor = extract('语音小编')
            self._image_editor = extract('图片小编')
            self._video_editor = extract('视频小编')
            self._broadcast_editor = extract('广播小编')
            self._journal_chief_editor = extract('吧刊主编')
            self._journal_editor = extract('吧刊小编')
            self._profess_admin = extract('职业吧主')
            self._fourth_admin = extract('第四吧主')

        else:
            self._admin = []
            self._manager = []
            self._voice_editor = []
            self._image_editor = []
            self._video_editor = []
            self._broadcast_editor = []
            self._journal_chief_editor = []
            self._journal_editor = []
            self._profess_admin = []
            self._fourth_admin = []

    def __repr__(self) -> str:
        return str(
            {
                'admin': self._admin,
                'manager': self._manager,
                'voice_editor': self._voice_editor,
                'image_editor': self._image_editor,
                'video_editor': self._video_editor,
                'broadcast_editor': self._broadcast_editor,
                'journal_chief_editor': self._journal_chief_editor,
                'journal_editor': self._journal_editor,
                'profess_admin': self._profess_admin,
                'fourth_admin': self._fourth_admin,
            }
        )

    @property
    def all(self) -> List[UserInfo_bawu]:
        """
        所有吧务
        """

        return self._all

    @property
    def admin(self) -> List[UserInfo_bawu]:
        """
        大吧主
        """

        return self._admin

    @property
    def manager(self) -> List[UserInfo_bawu]:
        """
        小吧主
        """

        return self._manager

    @property
    def voice_editor(self) -> List[UserInfo_bawu]:
        """
        语音小编
        """

        return self._voice_editor

    @property
    def video_editor(self) -> List[UserInfo_bawu]:
        """
        视频小编
        """

        return self._video_editor

    @property
    def image_editor(self) -> List[UserInfo_bawu]:
        """
        图片小编
        """

        return self._image_editor

    @property
    def broadcast_editor(self) -> List[UserInfo_bawu]:
        """
        广播小编
        """

        return self._broadcast_editor

    @property
    def journal_chief_editor(self) -> List[UserInfo_bawu]:
        """
        吧刊主编
        """

        return self._journal_chief_editor

    @property
    def journal_editor(self) -> List[UserInfo_bawu]:
        """
        吧刊小编
        """

        return self._journal_editor

    @property
    def profess_admin(self) -> List[UserInfo_bawu]:
        """
        职业吧主
        """

        return self._profess_admin

    @property
    def fourth_admin(self) -> List[UserInfo_bawu]:
        """
        第四吧主
        """

        return self._fourth_admin
