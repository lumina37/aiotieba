import sys

import yarl

from .._core import HttpCore
from .._helper import log_success, pack_form_request, parse_json, send_request
from ..const import APP_BASE_HOST, APP_SECURE_SCHEME
from ..exception import TiebaServerError


def parse_body(body: bytes) -> None:
    res_json = parse_json(body)
    if code := int(res_json['error_code']):
        raise TiebaServerError(code, res_json['error_msg'])
    if code := int(res_json['error']['errno']):
        raise TiebaServerError(code, res_json['error']['errmsg'])


async def request(http_core: HttpCore, fid: int) -> bool:
    data = [
        ('BDUSS', http_core.core._BDUSS),
        ('fid', fid),
        ('tbs', http_core.core._tbs),
    ]

    request = pack_form_request(
        http_core,
        yarl.URL.build(scheme=APP_SECURE_SCHEME, host=APP_BASE_HOST, path="/c/c/forum/like"),
        data,
    )

    __log__ = f"fid={fid}"

    body = await send_request(request, http_core.connector, read_bufsize=2 * 1024)
    parse_body(body)

    log_success(sys._getframe(1), __log__)
    return True
