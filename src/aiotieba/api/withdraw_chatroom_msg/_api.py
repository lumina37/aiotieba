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


async def request(
    http_core: HttpCore, fid: int, chatroom_id: int, msg_id: int, msg_key: str, user_id: int
) -> BoolResponse:
    data = [
        ("BDUSS", http_core.account.BDUSS),
        ("forum_id", fid),
        ("chatroom_id", chatroom_id),
        ("msg_id", msg_id),
        ("msg_key", msg_key),
        ("uid_to", user_id),
        ("tbs", http_core.account.tbs),
    ]

    request = http_core.pack_form_request(
        yarl.URL.build(scheme="https", host=APP_BASE_HOST, path="/c/c/chatroom/withdrawMsg"), data
    )

    body = await http_core.net_core.send(request)
    parse_body(body)

    return BoolResponse()
