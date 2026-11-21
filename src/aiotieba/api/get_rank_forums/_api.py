from __future__ import annotations

from typing import TYPE_CHECKING

import yarl

from ...const import WEB_BASE_HOST
from ...helper.parse import parse_html
from ._classdef import RankForums

if TYPE_CHECKING:
    from ...core import HttpCore
    from ...enums import RankForumType


def parse_body(body: bytes) -> RankForums:
    root = parse_html(body)
    rank_forums = RankForums.from_xml(root)

    return rank_forums


async def request(http_core: HttpCore, fname: str, pn: int, rank_type: RankForumType) -> RankForums:
    params = [
        ("kw", fname),
        ("type", int(rank_type)),
        ("pn", pn),
        ("ie", "utf-8"),
    ]

    request = http_core.pack_web_get_request(
        yarl.URL.build(scheme="https", host=WEB_BASE_HOST, path="/sign/index"), params
    )

    body = await http_core.net_core.send(request)
    return parse_body(body)
