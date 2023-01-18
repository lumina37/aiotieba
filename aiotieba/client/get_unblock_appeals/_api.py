import aiohttp
import yarl

from .._core import WEB_BASE_HOST, TbCore
from .._exception import TiebaServerError
from .._helper import pack_web_form_request, parse_json, send_request
from ._classdef import Appeals


async def request(
    connector: aiohttp.TCPConnector, core: TbCore, tbs: str, fname: str, fid: int, pn: int, rn: int
) -> bytes:

    data = [
        ('fn', fname),
        ('fid', fid),
        ('pn', pn),
        ('rn', rn),
        ('tbs', tbs),
    ]

    request = pack_web_form_request(
        core,
        yarl.URL.build(scheme="https", host=WEB_BASE_HOST, path="/mo/q/getBawuAppealList"),
        data,
    )

    body = await send_request(request, connector, read_bufsize=64 * 1024)

    return body


def parse_body(body: bytes) -> Appeals:
    res_json = parse_json(body)
    if code := res_json['no']:
        raise TiebaServerError(code, res_json['error'])

    appeals = Appeals()._init(res_json)

    return appeals
