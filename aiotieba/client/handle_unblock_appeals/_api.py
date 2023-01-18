from typing import List

import aiohttp
import yarl

from .._core import WEB_BASE_HOST, TbCore
from .._exception import TiebaServerError
from .._helper import pack_web_form_request, parse_json, send_request


async def request(
    connector: aiohttp.TCPConnector, core: TbCore, tbs: str, fname: str, fid: int, appeal_ids: List[int], refuse: bool
) -> bytes:

    data = (
        [
            ('fn', fname),
            ('fid', fid),
        ]
        + [(f'appeal_list[{i}]', appeal_id) for i, appeal_id in enumerate(appeal_ids)]
        + [
            ('refuse_reason', '_'),
            ('status', '2' if refuse else '1'),
            ('tbs', tbs),
        ]
    )

    request = pack_web_form_request(
        core,
        yarl.URL.build(scheme="https", host=WEB_BASE_HOST, path="/mo/q/multiAppealhandle"),
        data,
    )

    body = await send_request(request, connector, read_bufsize=32 * 1024)

    return body


def parse_body(body: bytes) -> None:
    res_json = parse_json(body)
    if code := res_json['no']:
        raise TiebaServerError(code, res_json['error'])
