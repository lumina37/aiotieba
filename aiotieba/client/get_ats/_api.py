import sys

import aiohttp
import yarl

from .._core import APP_BASE_HOST, TbCore
from .._exception import TiebaServerError
from .._helper import APP_SECURE_SCHEME, log_exception, pack_form_request, parse_json, send_request
from ._classdef import Ats


def parse_body(body: bytes) -> Ats:
    res_json = parse_json(body)
    if code := int(res_json['error_code']):
        raise TiebaServerError(code, res_json['error_msg'])

    ats = Ats()._init(res_json)

    return ats


async def request(connector: aiohttp.TCPConnector, core: TbCore, pn: int) -> Ats:

    data = [
        ('BDUSS', core._BDUSS),
        ('_client_version', core.main_version),
        ('pn', pn),
    ]

    request = pack_form_request(
        core,
        yarl.URL.build(scheme=APP_SECURE_SCHEME, host=APP_BASE_HOST, path="/c/u/feed/atme"),
        data,
    )

    try:
        body = await send_request(request, connector, read_bufsize=1024)
        ats = parse_body(body)

    except Exception as err:
        log_exception(sys._getframe(1), err)
        ats = Ats()._init_null()

    return ats
