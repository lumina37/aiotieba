from __future__ import annotations

from typing import TYPE_CHECKING
from urllib.parse import quote

import yarl

from ...const import APP_BASE_HOST
from ...exception import BoolResponse, TiebaServerError
from ...helper import pack_json, parse_json

if TYPE_CHECKING:
    from collections.abc import Iterable

    from ...core import HttpCore


def parse_body(body: bytes) -> None:
    res_json = parse_json(body)
    if code := int(res_json["error_code"]):
        raise TiebaServerError(code, res_json["error_msg"])


async def request(http_core: HttpCore, fids: Iterable[int]) -> BoolResponse:
    interest_list = {"": {str(fid): "" for fid in fids}}
    encoded_interest_list = quote(pack_json(interest_list), safe="")
    data = [
        ("BDUSS", http_core.account.BDUSS),
        ("interestList", encoded_interest_list),
    ]

    request = http_core.pack_form_request(
        yarl.URL.build(scheme="https", host=APP_BASE_HOST, path="/c/s/newUserInterestSave"), data
    )

    body = await http_core.net_core.send(request)
    parse_body(body)

    return BoolResponse()
