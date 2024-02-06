import dataclasses as dcs
from typing import Union


@dcs.dataclass
class UserInfo:
    """
    用户信息
    一般用于构造参数

    Args:
        id_ (str | int, optional): 用于快速构造UserInfo的自适应参数 输入用户名或portrait或user_id

    Attributes:
        user_id (int): user_id
        portrait (str): portrait
        user_name (str): 用户名
    """

    user_id: int = 0
    portrait: str = ''
    user_name: str = ''

    def __init__(self, id_: Union[str, int, None] = None) -> None:
        self.user_id = 0
        self.portrait = ''
        self.user_name = ''

        if id_ is not None:
            if isinstance(id_, int):
                self.user_id = id_
            else:
                self.portrait = id_
                if not self.portrait:
                    self.user_name = id_

    def __str__(self) -> str:
        if self.user_name:
            return self.user_name
        elif self.portrait:
            return self.portrait
        else:
            return str(self.user_id)

    def __eq__(self, obj: "UserInfo") -> bool:
        return self.user_id == obj.user_id

    def __hash__(self) -> int:
        return self.user_id

    def __bool__(self) -> bool:
        return bool(self.user_id)
