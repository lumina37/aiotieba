import yarl

from .._core import HttpCore
from .._helper import pack_form_request, parse_json, send_request
from ..const import APP_BASE_HOST, APP_SECURE_SCHEME
from ..exception import TiebaServerError
from ._classdef import Ats


def parse_body(body: bytes) -> Ats:
    res_json = parse_json(body)
    if code := int(res_json['error_code']):
        raise TiebaServerError(code, res_json['error_msg'])

    ats = Ats(res_json)

    return ats


async def request(http_core: HttpCore, pn: int) -> Ats:
    data = [
        ('BDUSS', http_core.core._BDUSS),
        ('_client_version', http_core.core.main_version),
        ('pn', pn),
    ]

    request = pack_form_request(
        http_core,
        yarl.URL.build(scheme=APP_SECURE_SCHEME, host=APP_BASE_HOST, path="/c/u/feed/atme"),
        data,
    )

    body = await send_request(request, http_core.connector, read_bufsize=1024)
    return parse_body(body)
