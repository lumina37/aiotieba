import sys

import yarl

from ...const import WEB_BASE_HOST
from ...core import HttpCore
from ...exception import TiebaServerError
from ...helper import log_success, parse_json
from ...request import pack_web_form_request, send_request


def parse_body(body: bytes) -> None:
    res_json = parse_json(body)
    if code := res_json['errno']:
        raise TiebaServerError(code, res_json['errmsg'])


async def request(http_core: HttpCore, fname: str, user_id: int) -> bool:
    data = [
        ('tbs', http_core.account._tbs),
        ('user_id', user_id),
        ('word', fname),
        ('ie', 'utf-8'),
    ]

    request = pack_web_form_request(
        http_core,
        yarl.URL.build(scheme="http", host=WEB_BASE_HOST, path="/bawu2/platform/addBlack"),
        data,
    )

    __log__ = f"fname={fname} user_id={user_id}"

    body = await send_request(request, http_core.network, read_bufsize=2 * 1024)
    parse_body(body)

    log_success(sys._getframe(1), __log__)
    return True
