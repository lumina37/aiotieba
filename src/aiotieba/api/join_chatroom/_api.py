from __future__ import annotations

from typing import TYPE_CHECKING

from ...core import CHAT_APPID, BLCPError, BLCPMethodID, BLCPServiceID

if TYPE_CHECKING:
    from ...core import BLCPCore


async def request(core: BLCPCore, chatroom_id: int) -> None:
    method = BLCPMethodID.JOIN_CAST
    request_data = {
        "method": method,
        "mcast_id": chatroom_id,
        "appid": CHAT_APPID,
        "uk": core.account.user.uk,
    }

    response = await core.request(BLCPServiceID.MCAST, method, request_data)
    if response.error_code != 0:
        raise BLCPError(f"加入聊天室失败 code={response.error_code} text={response.error_text!r}")

    err_code = response.payload["err_code"]
    if err_code != 0:
        raise BLCPError(f"加入聊天室失败 err_code={err_code}")
