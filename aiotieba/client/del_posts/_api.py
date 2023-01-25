import sys
from typing import List

import aiohttp
import yarl

from .._core import APP_BASE_HOST, TbCore
from .._exception import TiebaServerError
from .._helper import APP_SECURE_SCHEME, log_exception, log_success, pack_form_request, parse_json, send_request


def parse_body(body: bytes) -> None:
    res_json = parse_json(body)
    if code := int(res_json['error_code']):
        raise TiebaServerError(code, res_json['error_msg'])


async def request(connector: aiohttp.TCPConnector, core: TbCore, fid: int, pids: List[int], block: bool) -> bool:

    data = [
        ('BDUSS', core._BDUSS),
        ('forum_id', fid),
        ('post_ids', ','.join(str(pid) for pid in pids)),
        ('tbs', core._tbs),
        ('thread_id', '6'),
        ('type', '2' if block else '1'),
    ]

    request = pack_form_request(
        core,
        yarl.URL.build(scheme=APP_SECURE_SCHEME, host=APP_BASE_HOST, path="/c/c/bawu/multiDelPost"),
        data,
    )

    log_str = f"fid={fid} pids={pids}"
    frame = sys._getframe(1)

    try:
        body = await send_request(request, connector, read_bufsize=1024)
        parse_body(body)

    except Exception as err:
        log_exception(frame, err, log_str)
        return False

    log_success(frame, log_str)
    return True
