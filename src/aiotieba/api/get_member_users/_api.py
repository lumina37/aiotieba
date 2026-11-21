from __future__ import annotations

from typing import TYPE_CHECKING

import yarl

from ...const import WEB_BASE_HOST
from ...helper.parse import parse_html
from ._classdef import MemberUsers

if TYPE_CHECKING:
    from ...core import HttpCore


def parse_body(body: bytes) -> MemberUsers:
    root = parse_html(body)
    member_users = MemberUsers.from_xml(root)

    return member_users


async def request(http_core: HttpCore, fname: str, pn: int) -> MemberUsers:
    params = [
        ("word", fname),
        ("pn", pn),
        ("ie", "utf-8"),
    ]

    request = http_core.pack_web_get_request(
        yarl.URL.build(scheme="https", host=WEB_BASE_HOST, path="/bawu2/platform/listMemberInfo"), params
    )

    body = await http_core.net_core.send(request)
    return parse_body(body)
