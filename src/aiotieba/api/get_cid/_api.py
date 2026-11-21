from __future__ import annotations

import json
from typing import TYPE_CHECKING

import yarl

from ...const import APP_BASE_HOST
from ...exception import TiebaServerError

if TYPE_CHECKING:
    from ...core import HttpCore


def parse_body(body: bytes) -> list[dict[str, int]]:
    res_json = json.loads(body)
    if code := int(res_json["error_code"]):
        raise TiebaServerError(code, res_json["error_msg"])

    cates = res_json["cates"]

    return cates


async def request(http_core: HttpCore, fname: str) -> list[dict[str, int]]:
    data = [
        ("BDUSS", http_core.account.BDUSS),
        ("word", fname),
    ]

    request = http_core.pack_app_form_request(
        yarl.URL.build(scheme="https", host=APP_BASE_HOST, path="/c/c/bawu/goodlist"), data
    )

    body = await http_core.net_core.send(request)
    return parse_body(body)
