from __future__ import annotations

from typing import TYPE_CHECKING

import yarl

from ...const import WEB_BASE_HOST
from ...helper.parse import parse_html
from ._classdef import RankUsers

if TYPE_CHECKING:
    from ...core import HttpCore


def parse_body(body: bytes) -> RankUsers:
    root = parse_html(body)
    rank_users = RankUsers.from_xml(root)

    return rank_users


async def request(http_core: HttpCore, fname: str, pn: int) -> RankUsers:
    params = [
        ("kw", fname),
        ("pn", pn),
        ("ie", "utf-8"),
    ]

    request = http_core.pack_web_get_request(
        yarl.URL.build(scheme="https", host=WEB_BASE_HOST, path="/f/like/furank"), params
    )

    body = await http_core.net_core.send(request)
    return parse_body(body)
