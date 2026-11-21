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
    if "error" in res_json and (code := int(res_json["error"]["errno"])):
        raise TiebaServerError(code, res_json["error"]["errmsg"])


async def request(http_core: HttpCore, fid: int) -> BoolResponse:
    data = [
        ("fid", fid),
    ]

    request = http_core.pack_web_sign_form_request(
        yarl.URL.build(scheme="https", host=APP_BASE_HOST, path="/c/c/forum/like"),
        data,
        extra_headers={aiohttp.hdrs.REFERER: "https://tieba.baidu.com/"},
    )

    body = await http_core.net_core.send(request)
    parse_body(body)

    return BoolResponse()
