import httpx

from .._exception import TiebaServerError
from .common.helper import jsonlib, pack_form_request, sign
from .common.typedef import UserInfo


def pack_request(client: httpx.AsyncClient, bduss: str, version: str) -> httpx.Request:

    data = [
        ('BDUSS', bduss),
        ('_client_version', version),
    ]

    request = pack_form_request(client, "http://tiebac.baidu.com/c/s/initNickname", sign(data))

    return request


def parse_response(response: httpx.Response) -> UserInfo:
    response.raise_for_status()

    res_json = jsonlib.loads(response.content)
    if code := int(res_json['error_code']):
        raise TiebaServerError(code, res_json['error_msg'])

    user = UserInfo()
    user_dict = res_json['user_info']
    user._user_name = user_dict['user_name']
    user.nick_name = user_dict['name_show']
    user._tieba_uid = user_dict['tieba_uid']

    return user
