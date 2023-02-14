import yarl

from .._core import HttpCore
from .._helper import pack_form_request, parse_json, send_request
from ..const import APP_BASE_HOST, APP_SECURE_SCHEME
from ..exception import TiebaServerError
from ._classdef import Fans


def parse_body(body: bytes) -> Fans:
    res_json = parse_json(body)
    if code := int(res_json['error_code']):
        raise TiebaServerError(code, res_json['error_msg'])

    fans = Fans(res_json)

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

    __log__ = "user_id={user_id}"  # noqa: F841

    body = await send_request(request, http_core.connector, read_bufsize=16 * 1024)
    return parse_body(body)
