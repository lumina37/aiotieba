import httpx

from .._exception import TiebaServerError
from .common.helper import jsonlib


def pack_request(client: httpx.AsyncClient, fname: str) -> httpx.Request:
    request = httpx.Request(
        "GET",
        "http://tieba.baidu.com/f/commit/share/fnameShareApi",
        params={'fname': fname, 'ie': 'utf-8'},
        headers=client.headers,
        cookies=client.cookies,
    )

    return request


def parse_response(response: httpx.Response) -> int:
    res_json = jsonlib.loads(response.content)

    if int(res_json['no']):
        raise TiebaServerError(res_json['error'])

    if not (fid := int(res_json['data']['fid'])):
        raise TiebaServerError("fid is 0")

    return fid
