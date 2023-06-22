import sys
from typing import List

import yarl

from ...const import APP_BASE_HOST, APP_SECURE_SCHEME
from ...core import HttpCore
from ...exception import TiebaServerError
from ...helper import log_success, parse_json


def parse_body(body: bytes) -> None:
    res_json = parse_json(body)
    if code := int(res_json['error_code']):
        raise TiebaServerError(code, res_json['error_msg'])


async def request(http_core: HttpCore, fid: int, tids: List[int], block: bool) -> bool:
    data = [
        ('BDUSS', http_core.account._BDUSS),
        ('forum_id', fid),
        ('tbs', http_core.account._tbs),
        ('thread_ids', ','.join(map(str, tids))),
        ('type', '2' if block else '1'),
    ]

    request = http_core.pack_form_request(
        yarl.URL.build(scheme=APP_SECURE_SCHEME, host=APP_BASE_HOST, path="/c/c/bawu/multiDelThread"), data
    )

    __log__ = f"fid={fid} tids={tids}"

    body = await http_core.net_core.send_request(request, read_bufsize=1024)
    parse_body(body)

    log_success(sys._getframe(1), __log__)
    return True
