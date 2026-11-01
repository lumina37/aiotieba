from __future__ import annotations

from typing import TYPE_CHECKING
from urllib.parse import quote

import bs4
import yarl

from ...const import WEB_BASE_HOST
from ._classdef import BawuListMemberUsers

if TYPE_CHECKING:
    from ...core import HttpCore


def parse_body(body: bytes) -> BawuListMemberUsers:
    soup = bs4.BeautifulSoup(body, "lxml")
    bawu_memberlist_users = BawuListMemberUsers.from_xml(soup)

    return bawu_memberlist_users


async def request(
    http_core: HttpCore,
    fname: str,
    pn: int,
    user_name: str,
) -> BawuListMemberUsers:
    params = [
        ("word", fname),
        ("pn", pn),
        ("ie", "utf-8"),
    ]

    if user_name:
        user_name = quote(user_name)
        extend_params = [
            ("svalue", user_name),
            ("stype", "uname"),
        ]
        params += extend_params

    request = http_core.pack_web_get_request(
        yarl.URL.build(scheme="https", host=WEB_BASE_HOST, path="/bawu2/platform/listMember"), params
    )

    body = await http_core.net_core.send(request)
    return parse_body(body)
