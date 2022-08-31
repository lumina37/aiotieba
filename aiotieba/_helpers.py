import enum
import functools
import json
import sys
import time
from typing import Dict

from ._logger import LOG


def _json_decoder_hook(_dict: Dict):
    for key, value in _dict.items():
        if not value:
            _dict[key] = None
    return _dict


_DECODER = json.JSONDecoder(object_hook=_json_decoder_hook)
JSON_DECODE_FUNC = _DECODER.decode


class DelFlag(enum.IntEnum):
    DELETE = -2
    HIDE = -1
    NORMAL = 0
    WHITE = 1


class Punish(object):
    """
    处罚操作

    Fields:
        del_flag (DelFlag, optional): 处理结果. Defaults to DelFlag.NORMAL.
        block_days (int, optional): 封禁天数. Defaults to 0.
        note (str, optional): 处罚理由. Defaults to ''.
    """

    __slots__ = [
        'del_flag',
        'block_days',
        'note',
    ]

    def __init__(self, del_flag: DelFlag = DelFlag.NORMAL, block_days: int = 0, note: str = ''):
        self.del_flag: DelFlag = del_flag
        self.block_days: int = block_days
        if del_flag < DelFlag.NORMAL:
            line = sys._getframe(1).f_lineno
            self.note = f"L{line} {note}" if note else f"L{line}"
        else:
            self.note = note

    def __bool__(self) -> bool:
        if self.del_flag < DelFlag.NORMAL:
            return True
        if self.block_days:
            return True
        return False

    def __repr__(self) -> str:
        return str(
            {
                'del_flag': self.del_flag,
                'block_days': self.block_days,
                'note': self.note,
            }
        )


def alog_time(func) -> None:
    @functools.wraps(func)
    async def _(*args, **kwargs):
        start_time = time.perf_counter()
        res = await func(*args, **kwargs)
        LOG.debug(f"{func.__name__} time_cost: {time.perf_counter()-start_time:.4f}")
        return res

    return _
