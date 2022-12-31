import httpx

from .._exception import TiebaServerError
from .common.helper import jsonlib, raise_for_status, url


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

    res_json = jsonlib.loads(response.content)
    if code := int(res_json['no']):
        raise TiebaServerError(code, res_json['error'])

    if not (fid := int(res_json['data']['fid'])):
        raise TiebaServerError(-1, "fid is 0")

    return fid
