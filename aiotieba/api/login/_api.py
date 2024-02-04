from typing import Tuple

import yarl

from ...const import APP_BASE_HOST, APP_SECURE_SCHEME, MAIN_VERSION
from ...core import HttpCore
from ...exception import TiebaServerError
from ...helper import parse_json
from ._classdef import UserInfo_login


def parse_body(body: bytes) -> Tuple[UserInfo_login, str]:
    res_json = parse_json(body)
    if code := int(res_json['error_code']):
        raise TiebaServerError(code, res_json['error_msg'])

    user_dict = res_json['user']
    user = UserInfo_login.from_tbdata(user_dict)
    tbs = res_json['anti']['tbs']

    return user, tbs


async def request(http_core: HttpCore) -> Tuple[UserInfo_login, str]:
    data = [
        ('_client_version', MAIN_VERSION),
        ('bdusstoken', http_core.account.BDUSS),
    ]

    request = http_core.pack_form_request(
        yarl.URL.build(scheme=APP_SECURE_SCHEME, host=APP_BASE_HOST, path="/c/s/login"), data
    )

    body = await http_core.net_core.send_request(request, read_bufsize=1024)
    return parse_body(body)
