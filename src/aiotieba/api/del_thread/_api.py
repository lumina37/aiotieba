from __future__ import annotations

import json
from typing import TYPE_CHECKING

import aiohttp
import yarl

from ...const import APP_BASE_HOST
from ...exception import BoolResponse, TiebaServerError

if TYPE_CHECKING:
    from ...core import HttpCore


def parse_body(body: bytes) -> None:
    res_json = json.loads(body)
    if code := int(res_json["error_code"]):
        raise TiebaServerError(code, res_json["error_msg"])


async def request(http_core: HttpCore, fid: int, tid: int, is_hide: bool) -> BoolResponse:
    data = [
        ("fid", fid),
        ("is_frs_mask", int(is_hide)),
        ("z", tid),
    ]

    request = http_core.pack_web_sign_form_request(
        yarl.URL.build(scheme="https", host=APP_BASE_HOST, path="/c/c/bawu/delthread"),
        data,
        extra_headers={aiohttp.hdrs.REFERER: "https://tieba.baidu.com/"},
    )

    body = await http_core.net_core.send(request)
    parse_body(body)

    return BoolResponse()
