import yarl

from ...const import WEB_BASE_HOST
from ...core import HttpCore
from ...exception import TiebaServerError
from ...helper import parse_json
from ._classdef import Appeals


def parse_body(body: bytes) -> Appeals:
    res_json = parse_json(body)
    if code := res_json['no']:
        raise TiebaServerError(code, res_json['error'])

    appeals = Appeals.from_tbdata(res_json)

    return appeals


async def request(http_core: HttpCore, fid: int, pn: int, rn: int) -> Appeals:
    data = [
        ('fn', '-'),
        ('fid', fid),
        ('pn', pn),
        ('rn', rn),
        ('tbs', http_core.account.tbs),
    ]

    request = http_core.pack_web_form_request(
        yarl.URL.build(scheme="https", host=WEB_BASE_HOST, path="/mo/q/getBawuAppealList"), data
    )

    body = await http_core.net_core.send_request(request, read_bufsize=64 * 1024)
    return parse_body(body)
