import httpx

from .._exception import TiebaServerError
from .common.helper import jsonlib, pack_form_request, sign


def pack_request(client: httpx.AsyncClient, bduss: str, tbs: str, user_id: int) -> httpx.Request:

    data = [
        ('BDUSS', bduss),
        ('fans_uid', user_id),
        ('tbs', tbs),
    ]

    request = pack_form_request(client, "http://tiebac.baidu.com/c/c/user/removeFans", sign(data))

    return request


def parse_response(response: httpx.Response) -> None:
    response.raise_for_status()

    res_json = jsonlib.loads(response.content)
    if code := int(res_json['error_code']):
        raise TiebaServerError(code, res_json['error_msg'])
