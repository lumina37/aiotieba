import httpx

from .._exception import TiebaServerError
from .._helper import pack_form_request, parse_json, raise_for_status, url


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

    res_json = parse_json(response.content)
    if code := res_json['no']:
        raise TiebaServerError(code, res_json['error'])
