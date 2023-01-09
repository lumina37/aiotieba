import httpx

from .._exception import TiebaServerError
from .._helper import parse_json, raise_for_status, url
from ._classdef import SelfFollowForums


def pack_request(client: httpx.AsyncClient, pn: int) -> httpx.Request:
    request = httpx.Request(
        "GET",
        url("https", "tieba.baidu.com", "/mg/o/getForumHome"),
        params={'pn': pn, 'rn': '200'},
        headers=client.headers,
        cookies=client.cookies,
    )

    return request


def parse_response(response: httpx.Response) -> SelfFollowForums:
    raise_for_status(response)

    res_json = parse_json(response.content)
    if code := int(res_json['errno']):
        raise TiebaServerError(code, res_json['errmsg'])

    data_dict = res_json['data']['like_forum']
    self_follow_forums = SelfFollowForums()._init(data_dict)

    return self_follow_forums
