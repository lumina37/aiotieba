import yarl

from ...const import APP_BASE_HOST, APP_SECURE_SCHEME, MAIN_VERSION
from ...core import HttpCore
from ...exception import TiebaServerError
from ...helper import parse_json
from ._classdef import UserInfo_selfinit


def parse_body(body: bytes) -> UserInfo_selfinit:
    res_json = parse_json(body)
    if code := int(res_json['error_code']):
        raise TiebaServerError(code, res_json['error_msg'])

    user_dict = res_json['user_info']
    user = UserInfo_selfinit.from_tbdata(user_dict)

    return user


async def request(http_core: HttpCore) -> UserInfo_selfinit:
    data = [
        ('BDUSS', http_core.account.BDUSS),
        ('_client_version', MAIN_VERSION),
    ]

    request = http_core.pack_form_request(
        yarl.URL.build(scheme=APP_SECURE_SCHEME, host=APP_BASE_HOST, path="/c/s/initNickname"), data
    )

    body = await http_core.net_core.send_request(request, read_bufsize=1024)
    return parse_body(body)
