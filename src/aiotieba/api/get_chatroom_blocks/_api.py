from __future__ import annotations

from typing import TYPE_CHECKING

import yarl

from ...const import APP_BASE_HOST
from ...exception import TiebaServerError
from ...helper import parse_json
from ._classdef import ChatroomBlocks

if TYPE_CHECKING:
    from ...core import HttpCore


def parse_body(body: bytes) -> ChatroomBlocks:
    res_json = parse_json(body)
    if code := res_json["no"]:
        raise TiebaServerError(code, res_json["error"])

    blocks = ChatroomBlocks.from_json(res_json["data"])

    return blocks


async def request(http_core: HttpCore, chatroom_id: int, pn: int, rn: int) -> ChatroomBlocks:
    params = [
        ("chatroom_id", chatroom_id),
        ("pn", pn),
        ("rn", rn),
    ]

    request = http_core.pack_web_get_request(
        yarl.URL.build(scheme="https", host=APP_BASE_HOST, path="/mo/q/chat/getFobiddenList"), params
    )

    body = await http_core.net_core.send(request)

    return parse_body(body)
