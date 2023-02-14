import sys

import yarl

from .._core import HttpCore
from .._helper import log_success, pack_web_form_request, parse_json, send_request
from ..const import WEB_BASE_HOST
from ..exception import TiebaServerError


def parse_body(body: bytes) -> None:
    res_json = parse_json(body)
    if code := res_json['no']:
        raise TiebaServerError(code, res_json['error'])


async def request(http_core: HttpCore, fname: str, fid: int, user_id: int) -> bool:
    data = [
        ('fn', fname),
        ('fid', fid),
        ('block_un', ' '),
        ('block_uid', user_id),
        ('tbs', http_core.core._tbs),
    ]

    request = pack_web_form_request(
        http_core,
        yarl.URL.build(scheme="https", host=WEB_BASE_HOST, path="/mo/q/bawublockclear"),
        data,
    )

    __log__ = f"fname={fname} user_id={user_id}"

    body = await send_request(request, http_core.connector, read_bufsize=1024)
    parse_body(body)

    log_success(sys._getframe(1), __log__)
    return True
