import sys

import yarl

from ...const import APP_BASE_HOST, APP_SECURE_SCHEME
from ...core import HttpCore
from ...exception import TiebaServerError
from ...helper import log_success, parse_json


def parse_body(body: bytes) -> None:
    res_json = parse_json(body)
    if code := int(res_json['error_code']):
        raise TiebaServerError(code, res_json['error_msg'])


async def request(http_core: HttpCore, fname: str, fid: int, tid: int) -> bool:
    data = [
        ('BDUSS', http_core.account._BDUSS),
        ('fid', fid),
        ('tbs', http_core.account._tbs),
        ('word', fname),
        ('z', tid),
    ]

    request = http_core.pack_form_request(
        yarl.URL.build(scheme=APP_SECURE_SCHEME, host=APP_BASE_HOST, path="/c/c/bawu/commitgood"), data
    )

    __log__ = f"fname={fname} tid={tid}"

    body = await http_core.net_core.send_request(request, read_bufsize=1024)
    parse_body(body)

    log_success(sys._getframe(1), __log__)
    return True
