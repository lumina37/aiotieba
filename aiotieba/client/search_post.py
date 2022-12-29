import httpx

from .._exception import TiebaServerError
from .common.helper import jsonlib, pack_form_request, sign
from .common.typedef import Searches


def pack_request(
    client: httpx.AsyncClient,
    version: str,
    fname: str,
    query: str,
    pn: int,
    rn: int,
    query_type: int,
    only_thread: bool,
) -> httpx.Request:

    data = [
        ('_client_version', version),
        ('kw', fname),
        ('only_thread', int(only_thread)),
        ('pn', pn),
        ('rn', rn),
        ('sm', query_type),
        ('word', query),
    ]

    request = pack_form_request(client, "http://tiebac.baidu.com/c/s/searchpost", sign(data))

    return request


def parse_response(response: httpx.Response) -> Searches:
    response.raise_for_status()

    res_json = jsonlib.loads(response.content)
    if code := int(res_json['error_code']):
        raise TiebaServerError(code, res_json['error_msg'])

    searches = Searches(res_json)

    return searches
