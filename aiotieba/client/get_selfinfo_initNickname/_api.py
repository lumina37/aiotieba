import httpx

from .._classdef.core import TiebaCore
from .._exception import TiebaServerError
from .._helper import APP_BASE_HOST, pack_form_request, parse_json, raise_for_status, sign, url
from ._classdef import UserInfo_selfinit


def pack_request(client: httpx.AsyncClient, core: TiebaCore) -> httpx.Request:

    data = [
        ('BDUSS', core.BDUSS),
        ('_client_version', core.main_version),
    ]

    request = pack_form_request(
        client,
        url("http", APP_BASE_HOST, "/c/s/initNickname"),
        sign(data),
    )

    return request


def parse_response(response: httpx.Response) -> UserInfo_selfinit:
    raise_for_status(response)

    res_json = parse_json(response.content)
    if code := int(res_json['error_code']):
        raise TiebaServerError(code, res_json['error_msg'])

    user_dict = res_json['user_info']
    user = UserInfo_selfinit()._init(user_dict)

    return user
