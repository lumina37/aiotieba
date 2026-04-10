import yarl

from ...const import WEB_BASE_HOST
from ...core import HttpCore
from ...exception import TiebaServerError
from ...helper import parse_json
from ._classdef import SelfFollowForums


def parse_body(body: bytes) -> SelfFollowForums:
    res_json = parse_json(body)
    if code := res_json["error_code"]:
        raise TiebaServerError(code, res_json["error_msg"])

    self_follow_forums = SelfFollowForums.from_tbdata(res_json)

    return self_follow_forums


async def request(http_core: HttpCore, pn: int, rn: int) -> SelfFollowForums:
    data = [
        ("tbs", http_core.account.tbs),
        ("sort_type", 3),
        ("call_from", 3),
        ("page_no", pn),
        ("res_num", rn),
    ]

    request = http_core.pack_web_form_request(
        yarl.URL.build(scheme="https", host=WEB_BASE_HOST, path="/c/f/forum/forumGuide"),
        data,
        extra_headers=[("Subapp-Type", "hybrid")],
    )

    body = await http_core.net_core.send_request(request, read_bufsize=64 * 1024)
    return parse_body(body)
