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

    def _init(self, data_proto: TypeMessage) -> "UserInfo_bawu":
        self._user_id = data_proto.user_id
        self._portrait = data_proto.portrait
        self._user_name = data_proto.user_name
        self._nick_name_new = data_proto.name_show
        self._level = data_proto.user_level
        return self

    def _init_null(self) -> "UserInfo_bawu":
        self._user_id = 0
        self._portrait = ''
        self._user_name = ''
        self._nick_name_new = ''
        self._level = 0
        return self

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
