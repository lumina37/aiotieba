from typing import Tuple

import httpx

from .._exception import TiebaServerError
from .common.helper import jsonlib, pack_form_request
from .common.typedef import UserInfo


def pack_request(client: httpx.AsyncClient, version: str, bduss: str) -> httpx.Request:
    request = pack_form_request(
        client,
        "http://tiebac.baidu.com/c/s/login",
        [
            ('_client_version', version),
            ('bdusstoken', bduss)
        ],
    )

    return request


def parse_response(response: httpx.Response) -> Tuple[UserInfo, str]:
    res_json = jsonlib.loads(response.content)

    if int(res_json['error_code']):
        raise TiebaServerError(res_json['error_msg'])

    user = UserInfo()
    user_dict = res_json['user']
    user.user_id = user_dict['id']
    user.portrait = user_dict['portrait']
    user._user_name = user_dict['name']
    tbs = res_json['anti']['tbs']

    return user, tbs
