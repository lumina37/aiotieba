from __future__ import annotations

import dataclasses as dcs
from typing import TYPE_CHECKING, Self

from ...enums import ContentType
from .._classdef import Containers

if TYPE_CHECKING:
    from ..get_recovers._classdef import Recover


@dcs.dataclass
class RecoverReq:
    """
    待恢复对象的恢复请求

    Attributes:
        tid (int): 所在主题帖id
        pid (int): 待恢复对象的id 对主题帖该字段为0
        content_type (ContentType): 待恢复对象的类型
        is_hide (bool): True则解除屏蔽 False则恢复删帖
    """

    tid: int = 0
    pid: int = 0
    content_type: ContentType = ContentType.UNKNOWN
    is_hide: bool = False

    @classmethod
    def from_rec(cls, rec: Recover) -> Self:
        return cls(rec.tid, rec.pid, rec.content_type, rec.is_hide)


@dcs.dataclass
class RecoverReqs(Containers[RecoverReq]):
    """
    待恢复对象的恢复请求列表

    Attributes:
        objs (list[RecoverReq]): 恢复请求列表
    """
