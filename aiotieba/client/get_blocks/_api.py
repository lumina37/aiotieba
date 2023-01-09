import httpx

from .._exception import TiebaServerError
from .._helper import parse_json, raise_for_status, url
from ._classdef import Blocks


def pack_request(client: httpx.AsyncClient, fname: str, fid: int, name: str, pn: int) -> httpx.Request:
    request = httpx.Request(
        "GET",
        url("https", "tieba.baidu.com", "/mo/q/bawublock"),
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


def parse_response(response: httpx.Response) -> Blocks:
    raise_for_status(response)

    res_json = parse_json(response.content)
    if code := res_json['no']:
        raise TiebaServerError(code, res_json['error'])

    recovers = Blocks()._init(res_json)

    return recovers
