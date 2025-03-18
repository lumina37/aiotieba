import time

import yarl

from ._classdef import RoomList
from ...const import APP_BASE_HOST, CHAT_VERSION
from ...core import HttpCore
from ...exception import BoolResponse, TiebaServerError
from ...helper import parse_json


def parse_body(body: bytes) -> RoomList:
    res_json = parse_json(body)
    if code := int(res_json["error_code"]):
        raise TiebaServerError(code, res_json["error_msg"])
    roomlist = RoomList.from_tbdata(res_json)
    return roomlist



async def request(http_core: HttpCore, fid: int) -> RoomList:
    data = [
        ("BDUSS", http_core.account.BDUSS),
        ("_client_version", CHAT_VERSION),
        ("call_from", "frs"),
        ("fid", fid),
    ]

    request = http_core.pack_form_request(
        yarl.URL.build(scheme="https", host=APP_BASE_HOST, path="/c/f/chat/getRoomListByFid"), data,
    )

    body = await http_core.net_core.send_request(request, read_bufsize=1024)

    return parse_body(body)
