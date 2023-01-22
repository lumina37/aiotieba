import sys
from typing import Dict

import aiohttp
import yarl

from .._core import APP_BASE_HOST, TbCore
from .._exception import TiebaServerError
from .._helper import APP_SECURE_SCHEME, log_exception, pack_form_request, parse_json, send_request


def parse_body(body: bytes) -> Dict[str, str]:
    res_json = parse_json(body)
    if code := int(res_json['error_code']):
        raise TiebaServerError(code, res_json['error_msg'])

    cates = res_json['cates']

    return cates


async def request(connector: aiohttp.TCPConnector, core: TbCore, fname: str) -> Dict[str, str]:

    data = [
        ('BDUSS', core._BDUSS),
        ('word', fname),
    ]

    request = pack_form_request(
        core,
        yarl.URL.build(scheme=APP_SECURE_SCHEME, host=APP_BASE_HOST, path="/c/c/bawu/goodlist"),
        data,
    )

    try:
        body = await send_request(request, connector, read_bufsize=1024)
        cates = parse_body(body)

    except Exception as err:
        log_exception(sys._getframe(1), err, f"fname={fname}")
        cates = {}

    return cates
