import sys

import yarl

from .._core import WEB_BASE_HOST, HttpCore
from .._helper import log_exception, pack_web_form_request, parse_json, send_request
from ..exception import TiebaServerError
from ._classdef import Appeals


def parse_body(body: bytes) -> Appeals:
    res_json = parse_json(body)
    if code := res_json['no']:
        raise TiebaServerError(code, res_json['error'])

    appeals = Appeals()._init(res_json)

    return appeals


async def request(http_core: HttpCore, fname: str, fid: int, pn: int, rn: int) -> Appeals:

    data = [
        ('fn', fname),
        ('fid', fid),
        ('pn', pn),
        ('rn', rn),
        ('tbs', http_core.core._tbs),
    ]

    request = pack_web_form_request(
        http_core,
        yarl.URL.build(scheme="https", host=WEB_BASE_HOST, path="/mo/q/getBawuAppealList"),
        data,
    )

    try:
        body = await send_request(request, http_core.connector, read_bufsize=64 * 1024)
        appeals = parse_body(body)

    except Exception as err:
        log_exception(sys._getframe(1), err, f"fname={fname}")
        appeals = Appeals()._init_null()

    return appeals
