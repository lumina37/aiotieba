from typing import Union

from .._helper import is_portrait


class UserInfo(object):
    """
    用户信息
    一般用于构造参数

    Args:
        _id (str | int, optional): 用于快速构造UserInfo的自适应参数 输入用户名或portrait或user_id

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

    def __init__(self, _id: Union[str, int, None] = None) -> None:
        self._user_id = 0
        self._portrait = ''
        self._user_name = ''

        if _id is not None:
            if isinstance(_id, int):
                self._user_id = _id
            else:
                self.portrait = _id
                if not self.portrait:
                    self._user_name = _id

    def __str__(self) -> str:
        if self._user_name:
            return self._user_name
        elif self._portrait:
            return self._portrait
        else:
            return str(self._user_id)

    def __repr__(self) -> str:
        return str(
            {
                'user_id': self.user_id,
                'user_name': self.user_name,
                'portrait': self.portrait,
            }
        )

    def __eq__(self, obj: "UserInfo") -> bool:
        return self._user_id == obj._user_id

    def __hash__(self) -> int:
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

    @user_id.setter
    def user_id(self, new_user_id: int) -> None:
        self._user_id = int(new_user_id) if new_user_id else 0

    @property
    def portrait(self) -> str:
        """
        用户portrait

        Note:
            唯一 不可变 不可为空
        """

        return self._portrait

    @portrait.setter
    def portrait(self, new_portrait: str) -> None:

        if new_portrait and is_portrait(new_portrait):

            beg_start = 33
            q_index = new_portrait.find('?', beg_start)
            and_index = new_portrait.find('&', beg_start)

            if q_index != -1:
                self._portrait = new_portrait[:q_index]
            elif and_index != -1:
                self._portrait = new_portrait[:and_index]
            else:
                self._portrait = new_portrait

        else:
            self._portrait = ''

    @property
    def user_name(self) -> str:
        """
        用户名

        Note:
            唯一 可变 可为空
            请注意与用户昵称区分
        """

        return self._user_name

    @user_name.setter
    def user_name(self, new_user_name: str) -> None:
        self._user_name = new_user_name
