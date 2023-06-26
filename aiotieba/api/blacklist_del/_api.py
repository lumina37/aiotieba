import sys

import yarl

from ...const import WEB_BASE_HOST
from ...core import HttpCore
from ...exception import TiebaServerError
from ...helper import log_success, parse_json


def parse_body(body: bytes) -> None:
    res_json = parse_json(body)
    if code := res_json['errno']:
        raise TiebaServerError(code, res_json['errmsg'])


async def request(http_core: HttpCore, fname: str, user_id: int) -> bool:
    data = [
        ('word', fname),
        ('tbs', http_core.account._tbs),
        ('list[]', user_id),
        ('ie', 'utf-8'),
    ]

    request = http_core.pack_web_form_request(
        yarl.URL.build(scheme="http", host=WEB_BASE_HOST, path="/bawu2/platform/cancelBlack"), data
    )

    __log__ = f"fname={fname} user_id={user_id}"

    body = await http_core.net_core.send_request(request, read_bufsize=2 * 1024)
    parse_body(body)

    log_success(sys._getframe(1), __log__)
    return True
