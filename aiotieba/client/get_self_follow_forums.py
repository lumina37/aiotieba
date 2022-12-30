import httpx

from .._exception import TiebaServerError
from .common.helper import jsonlib
from .common.typedef import SelfFollowForums


def pack_request(client: httpx.AsyncClient, pn: int) -> httpx.Request:
    request = httpx.Request(
        "GET",
        "https://tieba.baidu.com/mg/o/getForumHome",
        params={'pn': pn, 'rn': '200'},
        headers=client.headers,
        cookies=client.cookies,
    )

    return request


def parse_response(response: httpx.Response) -> SelfFollowForums:
    response.raise_for_status()

    res_json = jsonlib.loads(response.content)
    if code := int(res_json['errno']):
        raise TiebaServerError(code, res_json['errmsg'])

    self_follow_forums = SelfFollowForums(res_json)

    return self_follow_forums
