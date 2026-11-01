from __future__ import annotations

from typing import TYPE_CHECKING

from ...const import CHAT_VERSION
from ...core import BlcpLoginError, BlcpMethodID, BlcpRequest, BlcpServiceID, JsonBody
from ...helper.crypto import enuid

if TYPE_CHECKING:
    from ...core import BlcpCore


async def request(core: BlcpCore) -> None:
    account = core.account
    request_data = {
        "params": {
            "appname": "tieba",
            "sid": account.sample_id,
            "ua": f"900_1600_android_{CHAT_VERSION}_240",
            "uid": enuid(account.cuid_galaxy2),
            "cfrom": "1008550l",
            "from": "1008550l",
            "network": "1_-1",
            "p_sv": "32",
            "mps": "",
            "mpv": "1",
            "c3_aid": account.c3_aid,
            "type_id": "0",
        },
        "filter": {
            "aps": {"cpu_abi": "armeabi-v7a"},
            "command": {"step": "0"},
        },
    }

    request = BlcpRequest.create(BlcpServiceID.CLOUD_CONTROL, BlcpMethodID.LOGIN, JsonBody(request_data))
    response = await core.send(request)
    if response.error_code != 0:
        raise BlcpLoginError(f"Cloud control login failed: code={response.error_code} text={response.error_text!r}")

    errno = int(response.payload["errno"])
    if errno != 0:
        raise BlcpLoginError(f"Cloud control login failed: errno={errno}")
