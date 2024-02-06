import yarl

from ...const import APP_BASE_HOST, APP_SECURE_SCHEME, WEB_BASE_HOST
from ...core import HttpCore
from ...exception import BoolResponse, TiebaServerError
from ...helper import parse_json


def parse_body_web(body: bytes) -> None:
    res_json = parse_json(body)
    if code := res_json['no']:
        raise TiebaServerError(code, res_json['error'])


async def request_web(http_core: HttpCore, act_type: str) -> BoolResponse:
    data = [
        ('tbs', http_core.account.tbs),
        ('act_type', act_type),
        ('cuid', '-'),
    ]

    request = http_core.pack_web_form_request(
        yarl.URL.build(scheme="https", host=WEB_BASE_HOST, path="/mo/q/usergrowth/commitUGTaskInfo"), data
    )

    body = await http_core.net_core.send_request(request, read_bufsize=1024)
    parse_body_web(body)

    return BoolResponse()


def parse_body_app(body: bytes) -> None:
    res_json = parse_json(body)
    if code := int(res_json['error_code']):
        raise TiebaServerError(code, res_json['error_msg'])


async def request_app(http_core: HttpCore, act_type: str) -> BoolResponse:
    data = [
        ('BDUSS', http_core.account.BDUSS),
        ('act_type', act_type),
        ('cuid', '-'),
        ('tbs', http_core.account.tbs),
    ]

    request = http_core.pack_form_request(
        yarl.URL.build(scheme=APP_SECURE_SCHEME, host=APP_BASE_HOST, path="/c/c/user/commitUGTaskInfo"), data
    )

    body = await http_core.net_core.send_request(request, read_bufsize=1024)
    parse_body_app(body)

    return BoolResponse()
