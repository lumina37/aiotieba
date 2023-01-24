import sys

import aiohttp
import yarl

from .._core import APP_BASE_HOST, TbCore
from .._exception import TiebaServerError
from .._helper import APP_SECURE_SCHEME, log_exception, pack_form_request, parse_json, send_request


def parse_body(body: bytes) -> str:
    res_json = parse_json(body)
    if code := int(res_json['error_code']):
        raise TiebaServerError(code, res_json['error_msg'])

    client_id = res_json['client']['client_id']

    return client_id


async def request(connector: aiohttp.TCPConnector, core: TbCore) -> str:

    data = [('BDUSS', core._BDUSS)]

    request = pack_form_request(
        core,
        yarl.URL.build(scheme=APP_SECURE_SCHEME, host=APP_BASE_HOST, path="/c/s/sync"),
        data,
    )

    try:
        body = await send_request(request, connector, read_bufsize=64 * 1024)
        client_id = parse_body(body)

    except Exception as err:
        log_exception(sys._getframe(1), err)
        client_id = ''

    return client_id
