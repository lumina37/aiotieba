import yarl

from ...const import APP_BASE_HOST, APP_INSECURE_SCHEME, MAIN_VERSION
from ...core import HttpCore
from ...enums import SearchType
from ...exception import TiebaServerError
from ...helper import parse_json
from ._classdef import ExactSearches


def parse_body(body: bytes) -> ExactSearches:
    res_json = parse_json(body)
    if code := int(res_json['error_code']):
        raise TiebaServerError(code, res_json['error_msg'])

    searches = ExactSearches.from_tbdata(res_json)

    return searches


async def request(
    http_core: HttpCore, fname: str, query: str, pn: int, rn: int, search_type: SearchType, only_thread: bool
) -> ExactSearches:
    data = [
        ('_client_version', MAIN_VERSION),
        ('kw', fname),
        ('only_thread', int(only_thread)),
        ('pn', pn),
        ('rn', rn),
        ('sm', search_type),
        ('word', query),
    ]

    request = http_core.pack_form_request(
        yarl.URL.build(scheme=APP_INSECURE_SCHEME, host=APP_BASE_HOST, path="/c/s/searchpost"), data
    )

    body = await http_core.net_core.send_request(request, read_bufsize=8 * 1024)
    return parse_body(body)
