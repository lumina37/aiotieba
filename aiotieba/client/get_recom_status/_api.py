import sys

import aiohttp
import yarl

from .._core import APP_BASE_HOST, TbCore
from .._exception import TiebaServerError
from .._helper import APP_SECURE_SCHEME, log_exception, pack_form_request, parse_json, send_request
from ._classdef import RecomStatus


def parse_body(body: bytes) -> RecomStatus:
    res_json = parse_json(body)
    if code := int(res_json['error_code']):
        raise TiebaServerError(code, res_json['error_msg'])

    status = RecomStatus()._init(res_json)

    return status


async def request(connector: aiohttp.TCPConnector, core: TbCore, fid: int) -> RecomStatus:

    data = [
        ('BDUSS', core._BDUSS),
        ('_client_version', core.main_version),
        ('forum_id', fid),
        ('pn', '1'),
        ('rn', '0'),
    ]

    request = pack_form_request(
        core,
        yarl.URL.build(scheme=APP_SECURE_SCHEME, host=APP_BASE_HOST, path="/c/f/bawu/getRecomThreadList"),
        data,
    )

    try:
        body = await send_request(request, connector, read_bufsize=2 * 1024)
        status = parse_body(body)

    except Exception as err:
        log_exception(sys._getframe(1), err, f"fid={fid}")
        status = RecomStatus()._init_null()

    return status
