from typing import Tuple

import httpx

from .._exception import TiebaServerError
from .common.core import TiebaCore
from .common.helper import APP_BASE_HOST, jsonlib, pack_form_request, raise_for_status, sign, url
from .common.typedef import UserInfo


def pack_request(client: httpx.AsyncClient, core: TiebaCore) -> httpx.Request:

    data = [
        ('_client_version', core.main_version),
        ('bdusstoken', core.BDUSS),
    ]

    request = pack_form_request(
        client,
        url("http", APP_BASE_HOST, "/c/s/login"),
        sign(data),
    )

    return request


def parse_response(response: httpx.Response) -> Tuple[UserInfo, str]:
    raise_for_status(response)

    res_json = jsonlib.loads(response.content)
    if code := int(res_json['error_code']):
        raise TiebaServerError(code, res_json['error_msg'])

    user = UserInfo()
    user_dict = res_json['user']
    user.user_id = user_dict['id']
    user.portrait = user_dict['portrait']
    user._user_name = user_dict['name']
    tbs = res_json['anti']['tbs']

    return user, tbs
