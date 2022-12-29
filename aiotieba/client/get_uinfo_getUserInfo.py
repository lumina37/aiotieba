import httpx

from .._exception import TiebaServerError
from .common.helper import jsonlib
from .common.typedef import UserInfo


def pack_request(client: httpx.AsyncClient, user_id: int) -> httpx.Request:
    request = httpx.Request(
        "GET",
        "http://tieba.baidu.com/im/pcmsg/query/getUserInfo",
        params={'chatUid': user_id},
        headers=client.headers,
        cookies=client.cookies,
    )

    return request


def parse_response(response: httpx.Response) -> UserInfo:
    response.raise_for_status()

    res_json = jsonlib.loads(response.content)
    if code := int(res_json['errno']):
        raise TiebaServerError(code, res_json['errmsg'])

    user_dict = res_json['chatUser']

    user = UserInfo()
    user.portrait = user_dict['portrait']
    user._user_name = user_dict['uname']

    return user
