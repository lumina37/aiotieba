import httpx

from .._exception import TiebaServerError
from .common.helper import jsonlib, pack_form_request, sign


def pack_request(client: httpx.AsyncClient, bduss: str, fid: int, tid: int) -> httpx.Request:

    data = [
        ('BDUSS', bduss),
        ('forum_id', fid),
        ('thread_id', tid),
    ]

    request = pack_form_request(client, "http://tiebac.baidu.com/c/c/bawu/pushRecomToPersonalized", sign(data))

    return request


def parse_response(response: httpx.Response) -> None:
    response.raise_for_status()

    res_json = jsonlib.loads(response.content)
    if code := int(res_json['error_code']):
        raise TiebaServerError(code, res_json['error_msg'])
    if code := int(res_json['data']['is_push_success']) != 1:
        raise TiebaServerError(code, res_json['data']['msg'])
