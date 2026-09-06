from __future__ import annotations

from typing import TYPE_CHECKING

import yarl

from ...const import WEB_BASE_HOST
from ...exception import TiebaServerError
from ...helper import parse_json
from ...helper.crypto import PC_SALT, sign
from ._classdef import SearchGlobals

if TYPE_CHECKING:
    from ...core import HttpCore

REFERER_GLOBAL = "https://tieba.baidu.com/f/search/res"


def parse_body(body: bytes) -> SearchGlobals:
    res_json = parse_json(body)
    if code := int(res_json["no"]):
        raise TiebaServerError(code, res_json.get("error", ""))

    searches = SearchGlobals.from_json(res_json["data"])

    return searches


async def request(
    http_core: HttpCore,
    query: str,
    pn: int,
    rn: int,
    sort: int,
) -> SearchGlobals:
    params = [
        ("word", query),
        ("pn", pn),
        ("rn", rn),
        ("st", sort),
        ("tt", 1),
        ("subapp_type", "pc"),
        ("_client_type", 20),
    ]
    params = sign(params, salt=PC_SALT)

    request = http_core.pack_web_get_request(
        yarl.URL.build(scheme="https", host=WEB_BASE_HOST, path="/mo/q/search/thread"),
        params,
        extra_headers=[("Referer", REFERER_GLOBAL)],
    )

    body = await http_core.net_core.send_request(request, read_bufsize=8 * 1024)
    return parse_body(body)
