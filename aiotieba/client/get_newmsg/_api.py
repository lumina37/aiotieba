import sys
from typing import Dict

import aiohttp
import yarl

from .._core import APP_BASE_HOST, TbCore
from .._exception import TiebaServerError
from .._helper import APP_SECURE_SCHEME, log_exception, pack_form_request, parse_json, send_request


def parse_body(body: bytes) -> Dict[str, bool]:
    res_json = parse_json(body)
    if code := int(res_json['error_code']):
        raise TiebaServerError(code, res_json['error_msg'])

    msg = {k: bool(int(v)) for k, v in res_json['message'].items()}

    return msg


async def request(connector: aiohttp.TCPConnector, core: TbCore) -> Dict[str, bool]:

    data = [('BDUSS', core._BDUSS)]

    request = pack_form_request(
        core,
        yarl.URL.build(scheme=APP_SECURE_SCHEME, host=APP_BASE_HOST, path="/c/s/msg"),
        data,
    )

    try:
        body = await send_request(request, connector, read_bufsize=1024)
        msg = parse_body(body)

    except Exception as err:
        log_exception(sys._getframe(1), err)
        msg = {
            'fans': False,
            'replyme': False,
            'atme': False,
            'agree': False,
            'pletter': False,
            'bookmark': False,
            'count': False,
        }

    return msg
