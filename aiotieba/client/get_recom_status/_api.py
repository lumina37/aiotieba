import yarl

from .._core import HttpCore
from .._helper import pack_form_request, parse_json, send_request
from ..const import APP_BASE_HOST, APP_SECURE_SCHEME
from ..exception import TiebaServerError
from ._classdef import RecomStatus


def parse_body(body: bytes) -> RecomStatus:
    res_json = parse_json(body)
    if code := int(res_json['error_code']):
        raise TiebaServerError(code, res_json['error_msg'])

    status = RecomStatus(res_json)

    return status


async def request(http_core: HttpCore, fid: int) -> RecomStatus:
    data = [
        ('BDUSS', http_core.core._BDUSS),
        ('_client_version', http_core.core.main_version),
        ('forum_id', fid),
        ('pn', '1'),
        ('rn', '0'),
    ]

    request = pack_form_request(
        http_core,
        yarl.URL.build(scheme=APP_SECURE_SCHEME, host=APP_BASE_HOST, path="/c/f/bawu/getRecomThreadList"),
        data,
    )

    __log__ = "fid={fid}"  # noqa: F841

    body = await send_request(request, http_core.connector, read_bufsize=2 * 1024)
    return parse_body(body)
