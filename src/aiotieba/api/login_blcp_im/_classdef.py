from __future__ import annotations

import dataclasses as dcs
from typing import TYPE_CHECKING, Self

if TYPE_CHECKING:
    from collections.abc import Mapping


@dcs.dataclass
class LoginIMResult:
    """
    IM登录结果

    Attributes:
        trigger_id (int): 群聊会话标识 作为群聊请求的origin_id字段
        uk (int): IM账号标识 作为群聊请求的uk字段
        user_id (int): user_id 用于生成baidu_uk
    """

    trigger_id: int = 0
    uk: int = 0
    user_id: int = 0

    @classmethod
    def from_json(cls, data_map: Mapping) -> Self:
        trigger_id = data_map["trigger_id"][0]
        uk = data_map["uk"]
        user_id = data_map["bd_uid"]

        return cls(trigger_id, uk, user_id)
