from __future__ import annotations

import time
from sys import maxsize as LONG_MAX
from typing import TYPE_CHECKING

from ...const import CHAT_VERSION
from ...core import CHAT_APPID, CHAT_SDK_VERSION
from ...exception import TiebaServerError
from ...helper import parse_json
from ...helper.crypto import sign
from ._classdef import ChatroomMsgs

if TYPE_CHECKING:
    from ...core import HttpCore


def parse_body(body: bytes) -> ChatroomMsgs:
    res_json = parse_json(body)
    if code := res_json["err_code"]:
        raise TiebaServerError(code, res_json["err_msg"])

    messages = ChatroomMsgs.from_json(res_json)

    return messages


async def request(http_core: HttpCore, chatroom_id: int) -> ChatroomMsgs:
    data = [
        ("appid", CHAT_APPID),
        ("mcast_id", chatroom_id),
        ("msgid_end", LONG_MAX),
        ("count", -60),
        ("category", 4),
        ("app_version", CHAT_VERSION),
        ("sdk_version", CHAT_SDK_VERSION),
        ("device_id", http_core.account.cuid_galaxy2),
        ("timestamp", int(time.time())),
    ]
    data = sign(data, salt=b"")

    request = http_core.pack_pim_request("/rest/3.0/im/fetch_mcast_msg_client", data, with_cookie=True)

    body = await http_core.net_core.send(request)

    return parse_body(body)
