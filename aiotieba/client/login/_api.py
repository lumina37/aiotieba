import sys
from typing import Tuple

import yarl

from .._core import APP_BASE_HOST, HttpCore
from .._helper import APP_SECURE_SCHEME, log_exception, pack_form_request, parse_json, send_request
from ..exception import TiebaServerError
from ._classdef import UserInfo_login


def parse_body(body: bytes) -> Tuple[UserInfo_login, str]:
    res_json = parse_json(body)
    if code := int(res_json['error_code']):
        raise TiebaServerError(code, res_json['error_msg'])

    user_dict = res_json['user']
    user = UserInfo_login()._init(user_dict)
    tbs = res_json['anti']['tbs']

    return user, tbs


async def request(http_core: HttpCore) -> Tuple[UserInfo_login, str]:

    data = [
        ('_client_version', http_core.core.main_version),
        ('bdusstoken', http_core.core._BDUSS),
    ]

    request = pack_form_request(
        http_core,
        yarl.URL.build(scheme=APP_SECURE_SCHEME, host=APP_BASE_HOST, path="/c/s/login"),
        data,
    )

    try:
        body = await send_request(request, http_core.connector, read_bufsize=1024)
        user, tbs = parse_body(body)

    except Exception as err:
        log_exception(sys._getframe(1), err)
        user = UserInfo_login()._init_null()
        tbs = ''

    return user, tbs
