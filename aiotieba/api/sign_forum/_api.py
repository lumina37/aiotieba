import sys

import yarl

from ...const import APP_BASE_HOST, APP_SECURE_SCHEME, MAIN_VERSION
from ...core import HttpCore
from ...exception import TiebaServerError, TiebaValueError
from ...helper import log_success, parse_json


def parse_body(body: bytes) -> None:
    res_json = parse_json(body)
    if code := int(res_json['error_code']):
        raise TiebaServerError(code, res_json['error_msg'])
    if int(res_json['user_info']['sign_bonus_point']) == 0:
        raise TiebaValueError("sign_bonus_point is 0")


async def request(http_core: HttpCore, fname: str) -> bool:
    data = [
        ('BDUSS', http_core.account._BDUSS),
        ('_client_version', MAIN_VERSION),
        ('kw', fname),
        ('tbs', http_core.account._tbs),
    ]

    request = http_core.pack_form_request(
        yarl.URL.build(scheme=APP_SECURE_SCHEME, host=APP_BASE_HOST, path="/c/c/forum/sign"), data
    )

    __log__ = f"fname={fname}"

    body = await http_core.net_core.send_request(request, read_bufsize=2 * 1024)
    parse_body(body)

    log_success(sys._getframe(1), __log__)
    return True
