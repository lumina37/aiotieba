from __future__ import annotations

import json
from typing import TYPE_CHECKING

import yarl

from ...const import APP_BASE_HOST
from ...exception import TiebaServerError
from ._classdef import FollowForums

if TYPE_CHECKING:
    from ...core import HttpCore


def parse_body(body: bytes) -> FollowForums:
    res_json = json.loads(body)
    if code := int(res_json["error_code"]):
        raise TiebaServerError(code, res_json["error_msg"])

    follow_forums = FollowForums.from_json(res_json)

    return follow_forums


async def request(http_core: HttpCore, user_id: int, pn: int, rn: int) -> FollowForums:
    data = [
        ("friend_uid", user_id),
        ("page_no", pn),
        ("page_size", rn),
    ]

    request = http_core.pack_web_sign_form_request(
        yarl.URL.build(scheme="https", host=APP_BASE_HOST, path="/c/f/forum/like"), data
    )

    body = await http_core.net_core.send(request)
    return parse_body(body)
