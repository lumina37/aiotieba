from __future__ import annotations

import json
from typing import TYPE_CHECKING

import yarl

from ...const import APP_BASE_HOST
from ...exception import TiebaServerError
from ._classdef import SearchInForums

if TYPE_CHECKING:
    from ...core import HttpCore
    from ...enums import SearchInForumType


def parse_body(body: bytes) -> SearchInForums:
    res_json = json.loads(body)
    if code := int(res_json["error_code"]):
        raise TiebaServerError(code, res_json["error_msg"])

    searches = SearchInForums.from_json(res_json)

    return searches


async def request(
    http_core: HttpCore, fname: str, query: str, pn: int, rn: int, search_type: SearchInForumType, only_thread: bool
) -> SearchInForums:
    data = [
        ("kw", fname),
        ("only_thread", int(only_thread)),
        ("pn", pn),
        ("rn", rn),
        ("sm", search_type),
        ("word", query),
    ]

    request = http_core.pack_web_sign_form_request(
        yarl.URL.build(scheme="http", host=APP_BASE_HOST, path="/c/s/searchpost"), data
    )

    body = await http_core.net_core.send(request)
    return parse_body(body)
