import yarl

from .._core import HttpCore
from .._helper import pack_web_get_request, parse_json, send_request
from ..const import WEB_BASE_HOST
from ..exception import TiebaServerError
from ._classdef import Blocks


def parse_body(body: bytes) -> Blocks:
    res_json = parse_json(body)
    if code := res_json['no']:
        raise TiebaServerError(code, res_json['error'])

    blocks = Blocks(res_json)

    return blocks


async def request(http_core: HttpCore, fname: str, fid: int, name: str, pn: int) -> Blocks:
    params = [
        ('fn', fname),
        ('fid', fid),
        ('word', name),
        ('is_ajax', '1'),
        ('pn', pn),
    ]

    request = pack_web_get_request(
        http_core,
        yarl.URL.build(scheme="https", host=WEB_BASE_HOST, path="/mo/q/bawublock"),
        params,
    )

    __log__ = "fname={fname}"  # noqa: F841

    body = await send_request(request, http_core.connector, read_bufsize=64 * 1024)
    return parse_body(body)
