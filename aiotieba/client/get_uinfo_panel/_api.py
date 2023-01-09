import httpx

from .._exception import TiebaServerError
from .._helper import is_portrait, parse_json, raise_for_status, url
from ._classdef import UserInfo_panel


def pack_request(client: httpx.AsyncClient, name_or_portrait: str) -> httpx.Request:

    params = {'id' if is_portrait(name_or_portrait) else 'un': name_or_portrait}

    request = httpx.Request(
        "GET",
        url("https", "tieba.baidu.com", "/home/get/panel"),
        params=params,
        headers=client.headers,
        cookies=client.cookies,
    )

    return request


def parse_response(response: httpx.Response) -> UserInfo_panel:
    raise_for_status(response)

    res_json = parse_json(response.content)
    if code := res_json['no']:
        raise TiebaServerError(code, res_json['error'])

    user_dict = res_json['data']
    user = UserInfo_panel()._init(user_dict)

    return user
