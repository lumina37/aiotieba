import yarl

from ...const import WEB_BASE_HOST
from ...core import HttpCore
from ...exception import TiebaServerError
from ...helper import parse_json
from ._classdef import SelfFollowForumsV1


def parse_body(body: bytes) -> SelfFollowForumsV1:
    res_json = parse_json(body)
    if code := res_json["errno"]:
        raise TiebaServerError(code, res_json["errmsg"])

    data_map = res_json["data"]["like_forum"]
    self_follow_forums = SelfFollowForumsV1.from_tbdata(data_map)

    return self_follow_forums


async def request(http_core: HttpCore, pn: int, rn: int) -> SelfFollowForumsV1:
    params = [
        ("pn", pn),
        ("rn", rn),
    ]

    request = http_core.pack_web_get_request(
        yarl.URL.build(scheme="https", host=WEB_BASE_HOST, path="/mg/o/getForumHome"), params
    )

    body = await http_core.net_core.send_request(request, read_bufsize=128 * 1024)
    return parse_body(body)
