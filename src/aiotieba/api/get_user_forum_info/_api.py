import yarl

from ...const import APP_BASE_HOST, MAIN_VERSION
from ...core import HttpCore
from ...exception import TiebaServerError
from ...helper import parse_json
from ._classdef import UserForumInfo


def parse_body(body: bytes) -> UserForumInfo:
    res_json = parse_json(body)
    if code := int(res_json.get("error_code", 0) or 0):
        err_msg = res_json.get("error_msg") or res_json.get("error") or res_json.get("errmsg") or ""
        raise TiebaServerError(code, err_msg)

    data_map = res_json.get("data", {})
    return UserForumInfo.from_tbdata(data_map)


async def request(http_core: HttpCore, forum_id: int, friend_portrait: str) -> UserForumInfo:
    data = [
        ("BDUSS", http_core.account.BDUSS),
        ("_client_version", MAIN_VERSION),
        ("forum_id", forum_id),
        ("friend_portrait", friend_portrait),
    ]

    request = http_core.pack_form_request(
        yarl.URL.build(scheme="https", host=APP_BASE_HOST, path="/c/f/forum/getUserForumLevelInfo"), data
    )

    body = await http_core.net_core.send_request(request, read_bufsize=4 * 1024)
    return parse_body(body)
