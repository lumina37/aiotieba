from typing import Mapping


class UserInfo_login(object):
    """
    用户信息

    Attributes:
        user_id (int): user_id
        portrait (str): portrait
        user_name (str): 用户名
    """

    __slots__ = [
        '_user_id',
        '_portrait',
        '_user_name',
    ]

    def _init(self, data_map: Mapping) -> "UserInfo_login":
        self._user_id = int(data_map['id'])
        self._portrait = data_map['portrait']
        self._user_name = data_map['name']
        return self

    def _init_null(self) -> "UserInfo_login":
        self._user_id = 0
        self._portrait = ''
        self._user_name = ''
        return self

    def __str__(self) -> str:
        return self._user_name or self._portrait or str(self._user_id)

    def __repr__(self) -> str:
        return str(
            {
                'user_id': self._user_id,
                'user_name': self._user_name,
                'portrait': self._portrait,
            }
        )

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
