import yarl

from ...const import APP_BASE_HOST, APP_SECURE_SCHEME, MAIN_VERSION
from ...core import HttpCore
from ...exception import BoolResponse, TiebaServerError, TiebaValueError
from ...helper import parse_json


def parse_body(body: bytes) -> None:
    res_json = parse_json(body)
    if code := int(res_json['error_code']):
        raise TiebaServerError(code, res_json['error_msg'])
    if int(res_json['user_info']['sign_bonus_point']) == 0:
        raise TiebaValueError("sign_bonus_point is 0")


async def request(http_core: HttpCore, fname: str) -> BoolResponse:
    data = [
        ('BDUSS', http_core.account.BDUSS),
        ('_client_version', MAIN_VERSION),
        ('kw', fname),
        ('tbs', http_core.account.tbs),
    ]

    request = http_core.pack_form_request(
        yarl.URL.build(scheme=APP_SECURE_SCHEME, host=APP_BASE_HOST, path="/c/c/forum/sign"), data
    )

    body = await http_core.net_core.send_request(request, read_bufsize=2 * 1024)
    parse_body(body)

    return BoolResponse
