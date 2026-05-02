import yarl

from ...const import WEB_BASE_HOST
from ...core import HttpCore
from ...exception import TiebaServerError
from ...helper import parse_json
from ...helper.crypto import PC_SALT, sign
from ._classdef import PcFollowForums


def parse_body(body: bytes) -> PcFollowForums:
    res_json = parse_json(body)
    if code := res_json["error_code"]:
        raise TiebaServerError(code, res_json["error_msg"])

    data_map = res_json["data"]
    follow_forums = PcFollowForums.from_json(data_map)

    return follow_forums


async def request(http_core: HttpCore, portrait: str, pn: int, rn: int) -> PcFollowForums:
    params = [
        ("portrait", portrait),
        ("pn", pn),
        ("rn", rn),
        ("subapp_type", "pc"),
        ("_client_type", 20),
    ]
    params = sign(params, salt=PC_SALT)

    request = http_core.pack_web_get_request(
        yarl.URL.build(scheme="https", host=WEB_BASE_HOST, path="/c/f/pc/myForumList"), params
    )

    body = await http_core.net_core.send_request(request, read_bufsize=16 * 1024)
    return parse_body(body)
