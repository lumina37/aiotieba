from __future__ import annotations

from typing import TYPE_CHECKING

import yarl

from ...const import APP_BASE_HOST
from ...exception import HTTPStatusError, TiebaServerError, TiebaValueError
from ...helper import parse_json

if TYPE_CHECKING:
    from ...core import HttpCore

COOKIE_KEY = "BAIDUID"


def parse_body(body: bytes) -> None:
    res_json = parse_json(body)
    if code := int(res_json["error_code"]):
        raise TiebaServerError(code, res_json["error_msg"])


async def request(http_core: HttpCore) -> str:
    request = http_core.pack_form_request(
        yarl.URL.build(scheme="https", host=APP_BASE_HOST, path="/c/c/forum/statClientStartTimes"),
        [("type", "1")],
    )

    response = await http_core.net_core.req2res(request)
    try:
        if response.status != 200:
            raise HTTPStatusError(response.status, response.reason)

        body = await response.content.read()
        cookie = response.cookies.get(COOKIE_KEY)

    finally:
        response.release()

    parse_body(body)

    if cookie is None:
        raise TiebaValueError(f"Missing {COOKIE_KEY} in response cookies")

    return cookie.value
