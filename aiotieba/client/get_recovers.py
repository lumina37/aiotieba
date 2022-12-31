import httpx

from .._exception import TiebaServerError
from .common.helper import jsonlib, raise_for_status, url
from .common.typedef import Recovers


def pack_request(client: httpx.AsyncClient, fname: str, fid: int, name: str, pn: int) -> httpx.Request:
    request = httpx.Request(
        "GET",
        url("https", "tieba.baidu.com", "/mo/q/bawurecover"),
        params={
            'fn': fname,
            'fid': fid,
            'word': name,
            'is_ajax': '1',
            'pn': pn,
        },
        headers=client.headers,
        cookies=client.cookies,
    )

    return request


def parse_response(response: httpx.Response) -> Recovers:
    raise_for_status(response)

    res_json = jsonlib.loads(response.content)
    if code := int(res_json['no']):
        raise TiebaServerError(code, res_json['error'])

    recovers = Recovers(res_json)

    return recovers
