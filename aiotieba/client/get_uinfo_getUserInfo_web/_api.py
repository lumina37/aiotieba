import httpx

from .._exception import TiebaServerError
from .._helper import parse_json, raise_for_status, url
from ._classdef import UserInfo_guinfo_web


def pack_request(client: httpx.AsyncClient, user_id: int) -> httpx.Request:
    request = httpx.Request(
        "GET",
        url("http", "tieba.baidu.com", "/im/pcmsg/query/getUserInfo"),
        params={'chatUid': user_id},
        headers=client.headers,
        cookies=client.cookies,
    )

    return request


def parse_response(response: httpx.Response) -> UserInfo_guinfo_web:
    raise_for_status(response)

    res_json = parse_json(response.content)
    if code := res_json['errno']:
        raise TiebaServerError(code, res_json['errmsg'])

    user_dict = res_json['chatUser']
    user = UserInfo_guinfo_web()._init(user_dict)

    return user
