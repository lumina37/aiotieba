import functools
import json
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


def alog_time(func) -> None:
    @functools.wraps(func)
    async def _(*args, **kwargs):
        start_time = time.perf_counter()
        res = await func(*args, **kwargs)
        LOG.debug(f"{func.__name__} time_cost: {time.perf_counter()-start_time:.4f}")
        return res

    return _
