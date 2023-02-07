import sys

import yarl

from .._core import APP_BASE_HOST, HttpCore
from .._helper import APP_SECURE_SCHEME, log_exception, pack_form_request, parse_json, send_request
from ..exception import TiebaServerError
from ._classdef import Fans


def parse_body(body: bytes) -> Fans:
    res_json = parse_json(body)
    if code := int(res_json['error_code']):
        raise TiebaServerError(code, res_json['error_msg'])

    fans = Fans()._init(res_json)

    return fans


async def request(http_core: HttpCore, user_id: int, pn: int) -> Fans:

    data = [
        ('BDUSS', http_core.core._BDUSS),
        ('_client_version', http_core.core.main_version),
        ('pn', pn),
        ('uid', user_id),
    ]

    request = pack_form_request(
        http_core,
        yarl.URL.build(scheme=APP_SECURE_SCHEME, host=APP_BASE_HOST, path="/c/u/fans/page"),
        data,
    )

    try:
        body = await send_request(request, http_core.connector, read_bufsize=16 * 1024)
        fans = parse_body(body)

    except Exception as err:
        log_exception(sys._getframe(1), err, f"user_id={user_id}")
        fans = Fans()._init_null()

    return fans
