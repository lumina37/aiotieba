from typing import Tuple

import yarl

from ...const import APP_BASE_HOST, APP_SECURE_SCHEME, MAIN_VERSION
from ...core import HttpCore
from ...exception import TiebaServerError
from ...helper import parse_json
from ...request import pack_form_request, send_request
from ._classdef import UserInfo_login


def parse_body(body: bytes) -> Tuple[UserInfo_login, str]:
    res_json = parse_json(body)
    if code := int(res_json['error_code']):
        raise TiebaServerError(code, res_json['error_msg'])

    user_dict = res_json['user']
    user = UserInfo_login(user_dict)
    tbs = res_json['anti']['tbs']

    return user, tbs


async def request(http_core: HttpCore) -> Tuple[UserInfo_login, str]:
    data = [
        ('_client_version', MAIN_VERSION),
        ('bdusstoken', http_core.account._BDUSS),
    ]

    request = pack_form_request(
        http_core,
        yarl.URL.build(scheme=APP_SECURE_SCHEME, host=APP_BASE_HOST, path="/c/s/login"),
        data,
    )

    body = await send_request(request, http_core.network, read_bufsize=1024)
    return parse_body(body)
