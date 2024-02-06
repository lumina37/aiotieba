import yarl

from ...const import APP_BASE_HOST, APP_SECURE_SCHEME, MAIN_VERSION
from ...core import HttpCore
from ...exception import TiebaServerError
from ...helper import parse_json
from ._classdef import Statistics


def parse_body(body: bytes) -> Statistics:
    res_json = parse_json(body)
    if code := int(res_json['error_code']):
        raise TiebaServerError(code, res_json['error_msg'])

    data_seq = res_json['data']
    stat = Statistics.from_tbdata(data_seq)

    return stat


async def request(http_core: HttpCore, fid: int) -> Statistics:
    data = [
        ('BDUSS', http_core.account.BDUSS),
        ('_client_version', MAIN_VERSION),
        ('forum_id', fid),
    ]

    request = http_core.pack_form_request(
        yarl.URL.build(scheme=APP_SECURE_SCHEME, host=APP_BASE_HOST, path="/c/f/forum/getforumdata"), data
    )

    body = await http_core.net_core.send_request(request, read_bufsize=4 * 1024)
    return parse_body(body)
