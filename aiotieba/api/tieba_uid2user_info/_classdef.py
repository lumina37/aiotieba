import dataclasses as dcs

from ...exception import TbErrorExt
from .._classdef import TypeMessage


@dcs.dataclass
class UserInfo_TUid(TbErrorExt):
    """
    用户信息

    Attributes:
        err (Exception | None): 捕获的异常

        user_id (int): user_id
        portrait (str): portrait
        user_name (str): 用户名
        nick_name_new (str): 新版昵称
        tieba_uid (int): 用户个人主页uid

        age (float): 吧龄
        sign (str): 个性签名

        is_god (bool): 是否大神

        nick_name (str): 用户昵称
        show_name (str): 显示名称
        log_name (str): 用于在日志中记录用户信息
    """

    user_id: int = 0
    portrait: str = ''
    user_name: str = ''
    nick_name_new: str = ''
    tieba_uid: int = 0

    age: float = 0.0
    sign: str = ""

    is_god: bool = False

    @staticmethod
    def from_tbdata(data_proto: TypeMessage) -> "UserInfo_TUid":
        user_id = data_proto.id
        portrait = data_proto.portrait
        if '?' in portrait:
            portrait = portrait[:-13]
        user_name = data_proto.name
        nick_name_new = data_proto.name_show
        tieba_uid = int(data_proto.tieba_uid)
        age = float(data_proto.tb_age)
        sign = data_proto.intro
        is_god = bool(data_proto.new_god_data.status)
        return UserInfo_TUid(user_id, portrait, user_name, nick_name_new, tieba_uid, age, sign, is_god)

    def __str__(self) -> str:
        return self.user_name or self.portrait or str(self.user_id)

    def __eq__(self, obj: "UserInfo_TUid") -> bool:
        return self.user_id == obj.user_id

    def __hash__(self) -> int:
        return self.user_id

    def __bool__(self) -> bool:
        return bool(self.user_id)

    @property
    def nick_name(self) -> str:
        return self.nick_name_new

    @property
    def show_name(self) -> str:
        return self.nick_name_new or self.user_name

    @property
    def log_name(self) -> str:
        if self.user_name:
            return self.user_name
        elif self.portrait:
            return f"{self.nick_name_new}/{self.portrait}"
        else:
            return str(self.user_id)
