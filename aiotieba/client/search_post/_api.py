import sys

import aiohttp
import yarl

from .._core import APP_BASE_HOST, TbCore
from .._exception import TiebaServerError
from .._helper import APP_INSECURE_SCHEME, log_exception, pack_form_request, parse_json, send_request
from ._classdef import Searches


def parse_body(body: bytes) -> Searches:
    res_json = parse_json(body)
    if code := int(res_json['error_code']):
        raise TiebaServerError(code, res_json['error_msg'])

    searches = Searches()._init(res_json)

    return searches


async def request(
    connector: aiohttp.TCPConnector,
    core: TbCore,
    fname: str,
    query: str,
    pn: int,
    rn: int,
    query_type: int,
    only_thread: bool,
) -> Searches:

    data = [
        ('_client_version', core.main_version),
        ('kw', fname),
        ('only_thread', int(only_thread)),
        ('pn', pn),
        ('rn', rn),
        ('sm', query_type),
        ('word', query),
    ]

    request = pack_form_request(
        core,
        yarl.URL.build(scheme=APP_INSECURE_SCHEME, host=APP_BASE_HOST, path="/c/s/searchpost"),
        data,
    )

    try:
        body = await send_request(request, connector, read_bufsize=8 * 1024)
        searches = parse_body(body)

    except Exception as err:
        log_exception(sys._getframe(1), err, f"fname={fname}")
        searches = Searches()._init_null()

    return searches
