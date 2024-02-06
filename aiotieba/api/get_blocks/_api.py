import yarl

from ...const import WEB_BASE_HOST
from ...core import HttpCore
from ...exception import TiebaServerError
from ...helper import parse_json
from ._classdef import Blocks


def parse_body(body: bytes) -> Blocks:
    res_json = parse_json(body)
    if code := res_json['no']:
        raise TiebaServerError(code, res_json['error'])

    blocks = Blocks.from_tbdata(res_json)

    return blocks


async def request(http_core: HttpCore, fid: int, name: str, pn: int) -> Blocks:
    params = [
        ('fn', '-'),
        ('fid', fid),
        ('word', name),
        ('is_ajax', 1),
        ('pn', pn),
    ]

    request = http_core.pack_web_get_request(
        yarl.URL.build(scheme="https", host=WEB_BASE_HOST, path="/mo/q/bawublock"), params
    )

    body = await http_core.net_core.send_request(request, read_bufsize=64 * 1024)
    return parse_body(body)
