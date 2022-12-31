import httpx

from .._exception import TiebaServerError
from .common.helper import jsonlib, pack_form_request, raise_for_status, url


def pack_request(client: httpx.AsyncClient, tbs: str, fname: str, fid: int, user_id: int) -> httpx.Request:

    data = [
        ('fn', fname),
        ('fid', fid),
        ('block_un', ' '),
        ('block_uid', user_id),
        ('tbs', tbs),
    ]

    request = pack_form_request(
        client,
        url("https", "tieba.baidu.com", "/mo/q/bawublockclear"),
        data,
    )

    return request


def parse_response(response: httpx.Response) -> None:
    raise_for_status(response)

    res_json = jsonlib.loads(response.content)
    if code := int(res_json['no']):
        raise TiebaServerError(code, res_json['error'])
