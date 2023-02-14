import yarl

from .._core import HttpCore
from .._helper import pack_web_get_request, parse_json, send_request
from ..const import WEB_BASE_HOST
from ..exception import TiebaServerError
from ._classdef import SelfFollowForums


def parse_body(body: bytes) -> SelfFollowForums:
    res_json = parse_json(body)
    if code := res_json['errno']:
        raise TiebaServerError(code, res_json['errmsg'])

    data_dict = res_json['data']['like_forum']
    self_follow_forums = SelfFollowForums(data_dict)

    return self_follow_forums


async def request(http_core: HttpCore, pn: int) -> SelfFollowForums:
    params = [
        ('pn', pn),
        ('rn', '200'),
    ]

    request = pack_web_get_request(
        http_core,
        yarl.URL.build(scheme="https", host=WEB_BASE_HOST, path="/mg/o/getForumHome"),
        params,
    )

    body = await send_request(request, http_core.connector, read_bufsize=128 * 1024)
    return parse_body(body)
