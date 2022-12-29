import httpx

from .._exception import TiebaServerError
from .common.helper import jsonlib, pack_form_request


def pack_request(client: httpx.AsyncClient, tbs: str, fname: str, user_id: int) -> httpx.Request:

    data = [
        ('word', fname),
        ('tbs', tbs),
        ('list[]', user_id),
        ('ie', 'utf-8'),
    ]

    request = pack_form_request(client, "http://tieba.baidu.com/bawu2/platform/cancelBlack", data)

    return request


def parse_response(response: httpx.Response) -> None:
    response.raise_for_status()

    res_json = jsonlib.loads(response.content)
    if code := int(res_json['errno']):
        raise TiebaServerError(code, res_json['errmsg'])
