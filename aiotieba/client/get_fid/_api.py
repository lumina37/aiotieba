import sys

import aiohttp
import yarl

from .._core import WEB_BASE_HOST, TbCore
from .._exception import TiebaServerError, TiebaValueError
from .._helper import log_exception, pack_web_get_request, parse_json, send_request


def parse_body(body: bytes) -> int:
    res_json = parse_json(body)
    if code := res_json['no']:
        raise TiebaServerError(code, res_json['error'])

    if not (fid := res_json['data']['fid']):
        raise TiebaValueError("fid is 0")

    return fid


async def request(connector: aiohttp.TCPConnector, core: TbCore, fname: str) -> int:

    params = [
        ('fname', fname),
        ('ie', 'utf-8'),
    ]

    request = pack_web_get_request(
        core,
        yarl.URL.build(scheme="http", host=WEB_BASE_HOST, path="/f/commit/share/fnameShareApi"),
        params,
    )

    try:
        body = await send_request(request, connector, read_bufsize=2 * 1024)
        fid = parse_body(body)

    except Exception as err:
        log_exception(sys._getframe(1), err, f"fname={fname}")
        fid = 0

    return fid
