from __future__ import annotations

from typing import TYPE_CHECKING

import yarl

from ...const import WEB_BASE_HOST
from ...exception import TiebaServerError
from ...helper import parse_json
from ._classdef import BawuBlacklistUsers

if TYPE_CHECKING:
    from ...core import HttpCore


def parse_body(body: bytes) -> BawuBlacklistUsers:
    res_json = parse_json(body)
    if code := res_json["no"]:
        raise TiebaServerError(code, res_json["error"])

    bawu_blacklist_users = BawuBlacklistUsers.from_json(res_json)

    return bawu_blacklist_users


async def request(http_core: HttpCore, fid: int, pn: int) -> BawuBlacklistUsers:
    params = [
        ("fn", "-"),
        ("fid", fid),
        ("word", ""),
        ("is_ajax", 1),
        ("pn", pn),
    ]

    request = http_core.pack_web_get_request(
        yarl.URL.build(scheme="https", host=WEB_BASE_HOST, path="/mo/q/bawublack"), params
    )

    body = await http_core.net_core.send(request)
    return parse_body(body)
