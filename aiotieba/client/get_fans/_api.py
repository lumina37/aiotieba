import aiohttp
import yarl

from .._core import APP_BASE_HOST, APP_SECURE_SCHEME, TbCore
from .._exception import TiebaServerError
from .._helper import pack_form_request, parse_json, send_request
from ._classdef import Fans


async def request(connector: aiohttp.TCPConnector, core: TbCore, user_id: int, pn: int) -> bytes:

    data = [
        ('BDUSS', core._BDUSS),
        ('_client_version', core.main_version),
        ('pn', pn),
        ('uid', user_id),
    ]

    request = pack_form_request(
        core,
        yarl.URL.build(scheme=APP_SECURE_SCHEME, host=APP_BASE_HOST, path="/c/u/fans/page"),
        data,
    )

    body = await send_request(request, connector, read_bufsize=16 * 1024)

    return body


def parse_body(body: bytes) -> Fans:
    res_json = parse_json(body)
    if code := int(res_json['error_code']):
        raise TiebaServerError(code, res_json['error_msg'])

    fans = Fans()._init(res_json)

    return fans
