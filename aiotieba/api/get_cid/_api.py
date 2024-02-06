from typing import Dict

import yarl

from ...const import APP_BASE_HOST, APP_SECURE_SCHEME
from ...core import HttpCore
from ...exception import TiebaServerError
from ...helper import parse_json


def parse_body(body: bytes) -> Dict[str, str]:
    res_json = parse_json(body)
    if code := int(res_json['error_code']):
        raise TiebaServerError(code, res_json['error_msg'])

    cates = res_json['cates']

    return cates


async def request(http_core: HttpCore, fname: str) -> Dict[str, str]:
    data = [
        ('BDUSS', http_core.account.BDUSS),
        ('word', fname),
    ]

    request = http_core.pack_form_request(
        yarl.URL.build(scheme=APP_SECURE_SCHEME, host=APP_BASE_HOST, path="/c/c/bawu/goodlist"), data
    )

    body = await http_core.net_core.send_request(request, read_bufsize=1024)
    return parse_body(body)
