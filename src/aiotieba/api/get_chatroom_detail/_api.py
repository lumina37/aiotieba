from __future__ import annotations

from typing import TYPE_CHECKING

import yarl

from ...const import APP_BASE_HOST, CHAT_VERSION
from ...exception import TiebaServerError
from ...helper import parse_json
from ...helper.crypto import APP_SALT, sign
from ._classdef import ChatroomDetail

if TYPE_CHECKING:
    from ...core import HttpCore


def parse_body(body: bytes) -> ChatroomDetail:
    res_json = parse_json(body)
    if code := int(res_json["error_code"]):
        raise TiebaServerError(code, res_json["error_msg"])

    data_map = res_json["data"]
    chatroom_detail = ChatroomDetail.from_json(data_map)

    return chatroom_detail


async def request(http_core: HttpCore, chatroom_id: int, last_msg_id: int = 0, last_time: int = 0) -> ChatroomDetail:
    params = [
        ("_client_version", CHAT_VERSION),
        ("chatroom_id", str(chatroom_id)),
    ]
    if last_msg_id:
        params.append(("last_msg_id", str(last_msg_id)))
    if last_time:
        params.append(("last_time", str(last_time)))
    params = sign(params, salt=APP_SALT)

    request = http_core.pack_web_get_request(
        yarl.URL.build(scheme="https", host=APP_BASE_HOST, path="/c/f/chat/getChatRoomDetail"), params
    )

    body = await http_core.net_core.send(request)

    return parse_body(body)
