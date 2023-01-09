import httpx

from .._exception import TiebaServerError
from .._helper import parse_json, raise_for_status, url
from ._classdef import UserInfo_json


def pack_request(client: httpx.AsyncClient, user_name: str) -> httpx.Request:
    request = httpx.Request(
        "GET",
        url("http", "tieba.baidu.com", "/i/sys/user_json"),
        params={'un': user_name, 'ie': 'utf-8'},
        headers=client.headers,
        cookies=client.cookies,
    )

    return request


def parse_response(response: httpx.Response) -> UserInfo_json:
    raise_for_status(response)
    if not response.content:
        raise TiebaServerError(-1, "empty response")

    text = response.content.decode('utf-8', errors='ignore')
    res_json = parse_json(text)

    user_dict = res_json['creator']
    user = UserInfo_json()._init(user_dict)

    return user
