import httpx

from .._classdef.core import TiebaCore
from .._exception import TiebaServerError
from .._helper import APP_BASE_HOST, pack_form_request, parse_json, raise_for_status, sign, url
from ._classdef import Searches


def pack_request(
    client: httpx.AsyncClient,
    core: TiebaCore,
    fname: str,
    query: str,
    pn: int,
    rn: int,
    query_type: int,
    only_thread: bool,
) -> httpx.Request:

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
        client,
        url("http", APP_BASE_HOST, "/c/s/searchpost"),
        sign(data),
    )

    return request


def parse_response(response: httpx.Response) -> Searches:
    raise_for_status(response)

    res_json = parse_json(response.content)
    if code := int(res_json['error_code']):
        raise TiebaServerError(code, res_json['error_msg'])

    searches = Searches()._init(res_json)

    return searches
