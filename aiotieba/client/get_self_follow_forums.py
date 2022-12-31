import httpx

from .._exception import TiebaServerError
from .common.helper import jsonlib, raise_for_status, url
from .common.typedef import SelfFollowForums


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

    res_json = jsonlib.loads(response.content)
    if code := int(res_json['errno']):
        raise TiebaServerError(code, res_json['errmsg'])

    self_follow_forums = SelfFollowForums(res_json)

    return self_follow_forums
