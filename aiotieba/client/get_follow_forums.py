import httpx

from .._exception import TiebaServerError
from .common.helper import jsonlib, pack_form_request, sign
from .common.typedef import FollowForums


def pack_request(client: httpx.AsyncClient, bduss: str, version: str, user_id: int, pn: int, rn: int) -> httpx.Request:

    data = [
        ('BDUSS', bduss),
        ('_client_version', version),
        ('friend_uid', user_id),
        ('page_no', pn),
        ('page_size', rn),
    ]

    request = pack_form_request(client, "http://tiebac.baidu.com/c/f/forum/like", sign(data))

    return request


def parse_response(response: httpx.Response) -> FollowForums:
    response.raise_for_status()

    res_json = jsonlib.loads(response.content)
    if code := int(res_json['error_code']):
        raise TiebaServerError(code, res_json['error_msg'])

    follow_forums = FollowForums(res_json)

    return follow_forums
