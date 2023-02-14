import yarl

from .._core import HttpCore
from .._helper import pack_form_request, parse_json, send_request
from ..const import APP_BASE_HOST, APP_INSECURE_SCHEME
from ..exception import TiebaServerError
from ._classdef import Searches


def parse_body(body: bytes) -> Searches:
    res_json = parse_json(body)
    if code := int(res_json['error_code']):
        raise TiebaServerError(code, res_json['error_msg'])

    searches = Searches(res_json)

    return searches


async def request(
    http_core: HttpCore, fname: str, query: str, pn: int, rn: int, query_type: int, only_thread: bool
) -> Searches:
    data = [
        ('_client_version', http_core.core.main_version),
        ('kw', fname),
        ('only_thread', int(only_thread)),
        ('pn', pn),
        ('rn', rn),
        ('sm', query_type),
        ('word', query),
    ]

    request = pack_form_request(
        http_core,
        yarl.URL.build(scheme=APP_INSECURE_SCHEME, host=APP_BASE_HOST, path="/c/s/searchpost"),
        data,
    )

    __log__ = "fname={fname}"  # noqa: F841

    body = await send_request(request, http_core.connector, read_bufsize=8 * 1024)
    return parse_body(body)
