import sys

import aiohttp
import yarl

from .._core import APP_BASE_HOST, TbCore
from .._exception import TiebaServerError
from .._helper import APP_SECURE_SCHEME, log_exception, log_success, pack_form_request, parse_json, send_request


def parse_body(body: bytes) -> None:
    res_json = parse_json(body)
    if code := int(res_json['error_code']):
        raise TiebaServerError(code, res_json['error_msg'])


async def request(connector: aiohttp.TCPConnector, core: TbCore, fname: str, fid: int, tid: int, is_set: bool) -> bool:

    data = [
        ('BDUSS', core._BDUSS),
        ('fid', fid),
        ('ntn', 'set' if is_set else ''),
        ('tbs', core._tbs),
        ('word', fname),
        ('z', tid),
    ]

    request = pack_form_request(
        core,
        yarl.URL.build(scheme=APP_SECURE_SCHEME, host=APP_BASE_HOST, path="/c/c/bawu/committop"),
        data,
    )

    log_str = f"fname={fname} tid={tid}"
    frame = sys._getframe(1)

    try:
        body = await send_request(request, connector, read_bufsize=1024)
        parse_body(body)

    except Exception as err:
        log_exception(frame, err, log_str)
        return False

    log_success(frame, log_str)
    return True
