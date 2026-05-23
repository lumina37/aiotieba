from __future__ import annotations

from typing import TYPE_CHECKING

import yarl

from ...const import WEB_BASE_HOST
from ...exception import TiebaServerError, TiebaValueError
from ...helper import parse_json

if TYPE_CHECKING:
    from ...core import HttpCore


def parse_body(body: bytes) -> int:
    res_json = parse_json(body)
    if code := res_json["no"]:
        raise TiebaServerError(code, res_json["error"])

    if not (fid := res_json["data"]["fid"]):
        raise TiebaValueError("fid is 0")

    return fid


async def request(http_core: HttpCore, fname: str) -> int:
    params = [
        ("fname", fname),
        ("ie", "utf-8"),
    ]

    request = http_core.pack_web_get_request(
        yarl.URL.build(scheme="http", host=WEB_BASE_HOST, path="/f/commit/share/fnameShareApi"), params
    )

    body = await http_core.net_core.send_request(request, read_bufsize=2 * 1024)
    return parse_body(body)
