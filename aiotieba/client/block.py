import httpx

from .._exception import TiebaServerError
from .common.helper import jsonlib, pack_form_request, sign


def pack_request(
    client: httpx.AsyncClient, bduss: str, tbs: str, fname: str, fid: int, portrait: str, day: int, reason: str
) -> httpx.Request:

    data = [
        ('BDUSS', bduss),
        ('day', day),
        ('fid', fid),
        ('ntn', 'banid'),
        ('portrait', portrait),
        ('reason', reason),
        ('tbs', tbs),
        ('word', fname),
        ('z', '6'),
    ]

    request = pack_form_request(client, "http://tiebac.baidu.com/c/c/bawu/commitprison", sign(data))

    return request


def parse_response(response: httpx.Response) -> None:
    response.raise_for_status()

    res_json = jsonlib.loads(response.content)
    if code := int(res_json['error_code']):
        raise TiebaServerError(code, res_json['error_msg'])
