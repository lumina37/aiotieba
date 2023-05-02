import sys
from typing import List

import yarl

from ...const import WEB_BASE_HOST
from ...core import HttpCore
from ...exception import TiebaServerError
from ...helper import log_success, parse_json
from ...request import pack_web_form_request, send_request


def parse_body(body: bytes) -> None:
    res_json = parse_json(body)
    if code := res_json['no']:
        raise TiebaServerError(code, res_json['error'])


async def request(http_core: HttpCore, fid: int, appeal_ids: List[int], refuse: bool) -> bool:
    data = (
        [
            ('fn', '-'),
            ('fid', fid),
        ]
        + [(f'appeal_list[{i}]', appeal_id) for i, appeal_id in enumerate(appeal_ids)]
        + [
            ('refuse_reason', '_'),
            ('status', '2' if refuse else '1'),
            ('tbs', http_core.account._tbs),
        ]
    )

    request = pack_web_form_request(
        http_core,
        yarl.URL.build(scheme="https", host=WEB_BASE_HOST, path="/mo/q/multiAppealhandle"),
        data,
    )

    __log__ = f"fid={fid}"

    body = await send_request(request, http_core.network, read_bufsize=1024)
    parse_body(body)

    log_success(sys._getframe(1), __log__)
    return True
