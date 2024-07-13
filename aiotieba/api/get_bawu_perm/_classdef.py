from __future__ import annotations

import dataclasses as dcs
from typing import Mapping

from ...enums import BawuPermType
from ...exception import TbErrorExt


@dcs.dataclass
class BawuPerm(TbErrorExt):
    """
    吧务已分配的权限

    Attributes:
        err (Exception | None): 捕获的异常
        perms (BawuPermType): 吧务已分配的权限
    """

    perms: BawuPermType = BawuPermType.NULL

    def from_tbdata(data_map: Mapping) -> BawuPerm:
        perms = BawuPermType.NULL

        for cate in ['category_user', 'category_thread']:
            perm_setting = data_map['perm_setting']
            for unblock_perm_dict in perm_setting[cate]:
                if not unblock_perm_dict['switch']:
                    continue

                perm_idx: int = unblock_perm_dict['perm'] - 2
                perm = [
                    BawuPermType.RECOVER_APPEAL,
                    BawuPermType.RECOVER,
                    BawuPermType.UNBLOCK,
                    BawuPermType.UNBLOCK_APPEAL,
                ][perm_idx]

                perms |= perm

        return BawuPerm(perms)
