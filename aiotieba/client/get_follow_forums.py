import httpx

from .._exception import TiebaServerError
from .common.core import TiebaCore
from .common.helper import APP_BASE_HOST, jsonlib, pack_form_request, raise_for_status, sign, url
from .common.typedef import FollowForums


def pack_request(client: httpx.AsyncClient, core: TiebaCore, user_id: int, pn: int, rn: int) -> httpx.Request:

    data = [
        ('BDUSS', core.BDUSS),
        ('_client_version', core.main_version),
        ('friend_uid', user_id),
        ('page_no', pn),
        ('page_size', rn),
    ]

    request = pack_form_request(
        client,
        url("http", APP_BASE_HOST, "/c/f/forum/like"),
        sign(data),
    )

    return request


def parse_response(response: httpx.Response) -> FollowForums:
    raise_for_status(response)

    res_json = jsonlib.loads(response.content)
    if code := int(res_json['error_code']):
        raise TiebaServerError(code, res_json['error_msg'])

    follow_forums = FollowForums(res_json)

    return follow_forums
