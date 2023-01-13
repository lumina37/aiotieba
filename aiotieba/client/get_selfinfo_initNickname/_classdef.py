from typing import Mapping


class UserInfo_selfinit(object):
    """
    用户信息

    Attributes:
        user_name (str): 用户名
        nick_name_old (str): 旧版昵称
        tieba_uid (int): 用户个人主页uid

        nick_name (str): 用户昵称
        show_name (str): 显示名称
        log_name (str): 用于在日志中记录用户信息
    """

    __slots__ = [
        '_user_name',
        '_nick_name_old',
        '_tieba_uid',
    ]

    def _init(self, data_map: Mapping) -> "UserInfo_selfinit":
        self._user_name = data_map['user_name']
        self._nick_name_old = data_map['name_show']
        self._tieba_uid = data_map['tieba_uid']
        return self

    def _init_null(self) -> "UserInfo_selfinit":
        self._nick_name_old = ''
        self._user_name = ''
        self._tieba_uid = 0
        return self

    def __str__(self) -> str:
        return self._user_name

    def __repr__(self) -> str:
        return str(
            {
                'user_name': self._user_name,
                'nick_name_old': self._nick_name_old,
                'tieba_uid': self._tieba_uid,
            }
        )

    def __eq__(self, obj: "UserInfo_selfinit") -> bool:
        return self._tieba_uid == obj._tieba_uid

    def __hash__(self) -> int:
        return self._tieba_uid

    def __int__(self) -> int:
        return self._tieba_uid

    def __bool__(self) -> bool:
        return bool(self._tieba_uid)

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
    def nick_name_old(self) -> str:
        """
        旧版昵称
        """

        return self._nick_name_old

    @property
    def tieba_uid(self) -> int:
        """
        用户个人主页uid

        Note:
            唯一 不可变 可为空
            请注意与user_id区分
        """

        return self._tieba_uid

    @property
    def nick_name(self) -> str:
        """
        用户昵称
        """

        return self._nick_name_old

    @property
    def log_name(self) -> str:
        """
        用于在日志中记录用户信息
        """

        if self._user_name:
            return self._user_name
        else:
            return f"{self._nick_name_old}/{self._tieba_uid}"
