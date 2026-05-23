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
    search_value: str,
) -> BawuListMemberUsers:
    params = [
        ("word", fname),
        ("pn", pn),
        ("ie", "utf-8"),
    ]

    if search_value:
        search_value = quote(search_value)
        extend_params = [
            ("svalue", search_value),
            ("stype", "uname"),
        ]
        params += extend_params

    request = http_core.pack_web_get_request(
        yarl.URL.build(scheme="https", host=WEB_BASE_HOST, path="/bawu2/platform/listMember"), params
    )

    body = await http_core.net_core.send_request(request, read_bufsize=32 * 1024)
    return parse_body(body)
