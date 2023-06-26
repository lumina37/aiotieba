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

    recovers = Recovers(res_json)

    return recovers


async def request(http_core: HttpCore, fid: int, name: str, pn: int) -> Recovers:
    params = [
        ('fn', '-'),
        ('fid', fid),
        ('word', name),
        ('is_ajax', '1'),
        ('pn', pn),
    ]

    request = http_core.pack_web_get_request(
        yarl.URL.build(scheme="https", host=WEB_BASE_HOST, path="/mo/q/bawurecover"), params
    )

    __log__ = "fid={fid}"  # noqa: F841

    body = await http_core.net_core.send_request(request, read_bufsize=64 * 1024)
    return parse_body(body)
