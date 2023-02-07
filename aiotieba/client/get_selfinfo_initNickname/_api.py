import sys

import yarl

from .._core import APP_BASE_HOST, HttpCore
from .._helper import APP_SECURE_SCHEME, log_exception, pack_form_request, parse_json, send_request
from ..exception import TiebaServerError
from ._classdef import UserInfo_selfinit


def parse_body(body: bytes) -> UserInfo_selfinit:
    res_json = parse_json(body)
    if code := int(res_json['error_code']):
        raise TiebaServerError(code, res_json['error_msg'])

    user_dict = res_json['user_info']
    user = UserInfo_selfinit()._init(user_dict)

    return user


async def request(http_core: HttpCore) -> UserInfo_selfinit:

    data = [
        ('BDUSS', http_core.core._BDUSS),
        ('_client_version', http_core.core.main_version),
    ]

    request = pack_form_request(
        http_core,
        yarl.URL.build(scheme=APP_SECURE_SCHEME, host=APP_BASE_HOST, path="/c/s/initNickname"),
        data,
    )

    try:
        body = await send_request(request, http_core.connector, read_bufsize=1024)
        user = parse_body(body)

    except Exception as err:
        log_exception(sys._getframe(1), err)
        user = UserInfo_selfinit()._init_null()

    return user
