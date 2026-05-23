from __future__ import annotations

from typing import TYPE_CHECKING

import yarl

from ...const import APP_BASE_HOST
from ...exception import BoolResponse, TiebaServerError
from ...helper import parse_json

if TYPE_CHECKING:
    from ...core import HttpCore


def parse_body(body: bytes) -> None:
    res_json = parse_json(body)
    if code := int(res_json["error_code"]):
        raise TiebaServerError(code, res_json["error_msg"])
    if code := int(res_json["errorno"]):
        raise TiebaServerError(code, res_json["errmsg"])


async def request(http_core: HttpCore, user_id: int) -> BoolResponse:
    data = [
        ("BDUSS", http_core.account.BDUSS),
        ("mute_user", user_id),
    ]

    request = http_core.pack_form_request(
        yarl.URL.build(scheme="https", host=APP_BASE_HOST, path="/c/c/user/userMuteAdd"), data
    )

    body = await http_core.net_core.send_request(request, read_bufsize=1024)
    parse_body(body)

    return BoolResponse()
