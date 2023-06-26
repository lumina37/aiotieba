import sys

import yarl

from ...const import APP_BASE_HOST, APP_SECURE_SCHEME, WEB_BASE_HOST
from ...core import HttpCore
from ...exception import TiebaServerError
from ...helper import log_success, parse_json


def parse_body_web(body: bytes) -> None:
    res_json = parse_json(body)
    if code := res_json['no']:
        raise TiebaServerError(code, res_json['error'])


async def request_web(http_core: HttpCore, act_type: str) -> bool:
    data = [
        ('tbs', http_core.account._tbs),
        ('act_type', act_type),
        ('cuid', '-'),
    ]

    request = http_core.pack_web_form_request(
        yarl.URL.build(scheme="https", host=WEB_BASE_HOST, path="/mo/q/usergrowth/commitUGTaskInfo"), data
    )

    body = await http_core.net_core.send_request(request, read_bufsize=1024)
    parse_body_web(body)

    log_success(sys._getframe(1))
    return True


def parse_body_app(body: bytes) -> None:
    res_json = parse_json(body)
    if code := int(res_json['error_code']):
        raise TiebaServerError(code, res_json['error_msg'])


async def request_app(http_core: HttpCore, act_type: str) -> bool:
    data = [
        ('BDUSS', http_core.account._BDUSS),
        ('act_type', act_type),
        ('cuid', '-'),
        ('tbs', http_core.account._tbs),
    ]

    request = http_core.pack_form_request(
        yarl.URL.build(scheme=APP_SECURE_SCHEME, host=APP_BASE_HOST, path="/c/c/user/commitUGTaskInfo"), data
    )

    body = await http_core.net_core.send_request(request, read_bufsize=1024)
    parse_body_app(body)

    log_success(sys._getframe(1))
    return True
