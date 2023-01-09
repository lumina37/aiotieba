import httpx

from .._exception import TiebaServerError
from .._helper import parse_json, raise_for_status, url


def pack_request(client: httpx.AsyncClient, fname: str) -> httpx.Request:
    request = httpx.Request(
        "GET",
        url("http", "tieba.baidu.com", "/f/commit/share/fnameShareApi"),
        params={'fname': fname, 'ie': 'utf-8'},
        headers=client.headers,
        cookies=client.cookies,
    )

    return request


def parse_response(response: httpx.Response) -> int:
    raise_for_status(response)

    res_json = parse_json(response.content)
    if code := res_json['no']:
        raise TiebaServerError(code, res_json['error'])

    if not (fid := res_json['data']['fid']):
        raise TiebaServerError(-1, "fid is 0")

    return fid
