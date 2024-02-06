from typing import Optional

import yarl

from ...const import WEB_BASE_HOST
from ...core import HttpCore
from ...exception import TiebaServerError
from ...helper import parse_json
from ._classdef import Recovers


def parse_body(body: bytes) -> Recovers:
    res_json = parse_json(body)
    if code := res_json['no']:
        raise TiebaServerError(code, res_json['error'])

    recovers = Recovers.from_tbdata(res_json)

    return recovers


async def request(http_core: HttpCore, fid: int, user_id: Optional[int], pn: int, rn: int) -> Recovers:
    params = [
        ('rn', rn),
        ('forum_id', fid),
        ('pn', pn),
        ('type', 1),
        ('sub_type', 1),
    ]
    if user_id:
        params.append(('uid', user_id))

    request = http_core.pack_web_get_request(
        yarl.URL.build(scheme="https", host=WEB_BASE_HOST, path="/mo/q/manage/getRecoverList"), params
    )

    body = await http_core.net_core.send_request(request, read_bufsize=64 * 1024)
    return parse_body(body)
