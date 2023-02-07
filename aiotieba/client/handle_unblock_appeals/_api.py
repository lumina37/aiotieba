import sys
from typing import List

import yarl

from .._core import WEB_BASE_HOST, HttpCore
from .._helper import log_exception, log_success, pack_web_form_request, parse_json, send_request
from ..exception import TiebaServerError


def parse_body(body: bytes) -> None:
    res_json = parse_json(body)
    if code := res_json['no']:
        raise TiebaServerError(code, res_json['error'])


async def request(http_core: HttpCore, fname: str, fid: int, appeal_ids: List[int], refuse: bool) -> bool:

    data = (
        [
            ('fn', fname),
            ('fid', fid),
        ]
        + [(f'appeal_list[{i}]', appeal_id) for i, appeal_id in enumerate(appeal_ids)]
        + [
            ('refuse_reason', '_'),
            ('status', '2' if refuse else '1'),
            ('tbs', http_core.core._tbs),
        ]
    )

    request = pack_web_form_request(
        http_core,
        yarl.URL.build(scheme="https", host=WEB_BASE_HOST, path="/mo/q/multiAppealhandle"),
        data,
    )

    log_str = f"fname={fname}"
    frame = sys._getframe(1)

    try:
        body = await send_request(request, http_core.connector, read_bufsize=1024)
        parse_body(body)

    except Exception as err:
        log_exception(frame, err, log_str)
        return False

    log_success(frame, log_str)
    return True
