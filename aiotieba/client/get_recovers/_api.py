import aiohttp
import yarl

from .._core import WEB_BASE_HOST, TbCore
from .._exception import TiebaServerError
from .._helper import pack_web_get_request, parse_json, send_request
from ._classdef import Recovers


async def request(connector: aiohttp.TCPConnector, core: TbCore, fname: str, fid: int, name: str, pn: int) -> bytes:

    params = [
        ('fn', fname),
        ('fid', fid),
        ('word', name),
        ('is_ajax', '1'),
        ('pn', pn),
    ]

    request = pack_web_get_request(
        core,
        yarl.URL.build(scheme="https", host=WEB_BASE_HOST, path="/mo/q/bawurecover"),
        params,
    )

    body = await send_request(request, connector, read_bufsize=64 * 1024)

    return body


def parse_body(body: bytes) -> Recovers:
    res_json = parse_json(body)
    if code := res_json['no']:
        raise TiebaServerError(code, res_json['error'])

    recovers = Recovers()._init(res_json)

    return recovers
