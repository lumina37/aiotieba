from __future__ import annotations

from typing import TYPE_CHECKING

from ...core import CHAT_APPID, BlcpError, BlcpMethodID, BlcpRequest, BlcpServiceID, JsonBody

if TYPE_CHECKING:
    from ...core import BlcpCore


async def request(core: BlcpCore, chatroom_id: int) -> None:
    method = BlcpMethodID.JOIN_CAST
    request_data = {
        "method": method,
        "mcast_id": chatroom_id,
        "appid": CHAT_APPID,
        "uk": core.account.user.uk,
    }

    request = BlcpRequest.create(BlcpServiceID.MCAST, method, JsonBody(request_data))
    response = await core.send(request)
    if response.error_code != 0:
        raise BlcpError(f"Failed to join chatroom: code={response.error_code} text={response.error_text!r}")

    err_code = response.payload["err_code"]
    if err_code != 0:
        raise BlcpError(f"Failed to join chatroom: err_code={err_code}")
