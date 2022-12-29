import httpx

from .._exception import TiebaServerError
from .common.helper import jsonlib, pack_form_request, sign
from .common.typedef import Ats


def pack_request(client: httpx.AsyncClient, bduss: str, version: str, pn: int) -> httpx.Request:

    data = [
        ('BDUSS', bduss),
        ('_client_version', version),
        ('pn', pn),
    ]

    request = pack_form_request(client, "http://tiebac.baidu.com/c/u/feed/atme", sign(data))

    return request


def parse_response(response: httpx.Response) -> Ats:
    response.raise_for_status()

    res_json = jsonlib.loads(response.content)
    if code := int(res_json['error_code']):
        raise TiebaServerError(code, res_json['error_msg'])

    ats = Ats(res_json)

    return ats
