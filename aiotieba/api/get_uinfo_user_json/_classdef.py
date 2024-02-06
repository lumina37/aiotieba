import dataclasses as dcs
from typing import Mapping

from ...exception import TbErrorExt


@dcs.dataclass
class UserInfo_json(TbErrorExt):
    """
    用户信息

    Attributes:
        err (Exception | None): 捕获的异常

        user_id (int): user_id
        portrait (str): portrait
        user_name (str): 用户名

        log_name (str): 用于在日志中记录用户信息
    """

    user_id: int = 0
    portrait: str = ''
    user_name: str = ''

    @staticmethod
    def from_tbdata(data_map: Mapping) -> "UserInfo_json":
        user_id = data_map['id']
        portrait = data_map['portrait']
        user_name = ''
        return UserInfo_json(user_id, portrait, user_name)

    def __str__(self) -> str:
        return self.user_name or self.portrait or str(self.user_id)

    def __eq__(self, obj: "UserInfo_json") -> bool:
        return self.user_id == obj.user_id

    def __hash__(self) -> int:
        return self.user_id

    def __bool__(self) -> bool:
        return bool(self.user_id)

    @property
    def log_name(self) -> str:
        return str(self)
