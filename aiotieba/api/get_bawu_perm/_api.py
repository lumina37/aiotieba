import yarl

from ...const import WEB_BASE_HOST
from ...core import HttpCore
from ...exception import TiebaServerError
from ...helper import parse_json
from ._classdef import BawuPerm


def parse_body(body: bytes) -> BawuPerm:
    res_json = parse_json(body)
    if code := res_json['no']:
        raise TiebaServerError(code, res_json['error'])

    data_dict = res_json['data']
    perm = BawuPerm.from_tbdata(data_dict)

    return perm


async def request(http_core: HttpCore, fid: int, portrait: str) -> BawuPerm:
    params = [
        ('forum_id', fid),
        ('portrait', portrait),
    ]

    request = http_core.pack_web_get_request(
        yarl.URL.build(scheme="https", host=WEB_BASE_HOST, path="/mo/q/getAuthToolPerm"), params
    )

    body = await http_core.net_core.send_request(request, read_bufsize=2 * 1024)
    return parse_body(body)
