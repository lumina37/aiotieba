from typing import List

import yarl

from ...const import APP_BASE_HOST, APP_SECURE_SCHEME
from ...core import HttpCore
from ...exception import BoolResponse, TiebaServerError
from ...helper import parse_json


def parse_body(body: bytes) -> None:
    res_json = parse_json(body)
    if code := int(res_json['error_code']):
        raise TiebaServerError(code, res_json['error_msg'])


async def request(http_core: HttpCore, fid: int, tid: int, pids: List[int], block: bool) -> BoolResponse:
    data = [
        ('BDUSS', http_core.account.BDUSS),
        ('forum_id', fid),
        ('post_ids', ','.join(map(str, pids))),
        ('tbs', http_core.account.tbs),
        ('thread_id', tid),
        ('type', 2 if block else 1),
    ]

    request = http_core.pack_form_request(
        yarl.URL.build(scheme=APP_SECURE_SCHEME, host=APP_BASE_HOST, path="/c/c/bawu/multiDelPost"), data
    )

    body = await http_core.net_core.send_request(request, read_bufsize=1024)
    parse_body(body)

    return BoolResponse()
