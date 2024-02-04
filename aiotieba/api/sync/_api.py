from typing import Tuple

import yarl

from ...const import APP_BASE_HOST, APP_SECURE_SCHEME, MAIN_VERSION
from ...core import HttpCore
from ...exception import TiebaServerError
from ...helper import parse_json


def parse_body(body: bytes) -> Tuple[str, str]:
    res_json = parse_json(body)
    if code := int(res_json['error_code']):
        raise TiebaServerError(code, res_json['error_msg'])

    client_id = res_json['client']['client_id']
    sample_id = res_json['wl_config']['sample_id']

    return client_id, sample_id


async def request(http_core: HttpCore) -> Tuple[str, str]:
    data = [
        ('BDUSS', http_core.account.BDUSS),
        ('_client_version', MAIN_VERSION),
        ('cuid', http_core.account.cuid_galaxy2),
    ]

    request = http_core.pack_form_request(
        yarl.URL.build(scheme=APP_SECURE_SCHEME, host=APP_BASE_HOST, path="/c/s/sync"), data
    )

    body = await http_core.net_core.send_request(request, read_bufsize=64 * 1024)
    return parse_body(body)
