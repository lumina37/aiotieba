import yarl

from ....const import LATEST_VERSION, WEB_BASE_HOST
from ....core import HttpCore
from ....exception import TiebaServerError
from ....helper import parse_json
from .._classdef import UserPostss


def parse_body(body: bytes) -> UserPostss:
    res_json = parse_json(body)
    if code := int(res_json["error_code"]):
        raise TiebaServerError(code, res_json["error_msg"])

    upostss = UserPostss.from_json(res_json)

    return upostss


async def request(http_core: HttpCore, user_id: int, pn: int, rn: int) -> UserPostss:
    data = [
        ("_client_version", LATEST_VERSION),
        ("res_num", rn),
        ("is_thread", 1),
        ("need_content", 1),
        ("is_view_card", 1),
        # ("forum_id", 0),
        ("uid", user_id),
        ("pn", pn),
        ("subapp_type", "hybrid"),
    ]

    request = http_core.pack_web_form_request(
        yarl.URL.build(scheme="https", host=WEB_BASE_HOST, path="/c/u/feed/userpost"),
        data,
        extra_headers=[("Subapp-Type", "hybrid")],
    )

    body = await http_core.net_core.send_request(request, read_bufsize=64 * 1024)
    return parse_body(body)
