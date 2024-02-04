import dataclasses as dcs
from typing import Mapping


@dcs.dataclass
class UserInfo_login:
    """
    用户信息

    Attributes:
        user_id (int): user_id
        portrait (str): portrait
        user_name (str): 用户名
    """

    user_id: int = 0
    portrait: str = ''
    user_name: str = ''

    @staticmethod
    def from_tbdata(data_map: Mapping) -> "UserInfo_login":
        user_id = int(data_map['id'])
        portrait = data_map['portrait']
        user_name = data_map['name']
        return UserInfo_login(user_id, portrait, user_name)

    def __str__(self) -> str:
        return self.user_name or self.portrait or str(self.user_id)

    def __hash__(self) -> int:
        return self.user_id

    def __bool__(self) -> bool:
        return bool(self.user_id)
