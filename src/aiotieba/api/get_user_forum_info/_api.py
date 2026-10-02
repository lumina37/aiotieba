from __future__ import annotations

from typing import TYPE_CHECKING

import yarl

from ...const import APP_BASE_HOST, LATEST_VERSION
from ...exception import TiebaServerError
from ...helper import parse_json
from ._classdef import UserForumInfo

if TYPE_CHECKING:
    from ...core import HttpCore


def parse_body(body: bytes) -> UserForumInfo:
    res_json = parse_json(body)
    if code := res_json["error_code"]:
        raise TiebaServerError(code, res_json["error_msg"])

    data_map = res_json["data"]
    user_forum_info = UserForumInfo.from_json(data_map)

    return user_forum_info


async def request(http_core: HttpCore, fid: int, friend_portrait: str) -> UserForumInfo:
    data = [
        ("BDUSS", http_core.account.BDUSS),
        ("_client_version", LATEST_VERSION),
        ("forum_id", fid),
        ("friend_portrait", friend_portrait),
    ]

    request = http_core.pack_form_request(
        yarl.URL.build(scheme="https", host=APP_BASE_HOST, path="/c/f/forum/getUserForumLevelInfo"), data
    )

    body = await http_core.net_core.send_request(request)
    return parse_body(body)
