import httpx

from .._exception import TiebaServerError
from .._helper import parse_json, raise_for_status, url
from ._classdef import Appeals


def pack_request(client: httpx.AsyncClient, tbs: str, fname: str, fid: int, pn: int, rn: int) -> httpx.Request:
    request = httpx.Request(
        "GET",
        url("https", "tieba.baidu.com", "/mo/q/getBawuAppealList"),
        params={
            'fn': fname,
            'fid': fid,
            'pn': pn,
            'rn': rn,
            'tbs': tbs,
        },
        headers=client.headers,
        cookies=client.cookies,
    )

    return request


def parse_response(response: httpx.Response) -> Appeals:
    raise_for_status(response)

    res_json = parse_json(response.content)
    if code := res_json['no']:
        raise TiebaServerError(code, res_json['error'])

    appeals = Appeals()._init(res_json)

    return appeals
