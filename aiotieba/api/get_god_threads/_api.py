import yarl

from ...const import WEB_BASE_HOST
from ...core import HttpCore
from ...exception import TiebaServerError
from ...helper import parse_json
from ._classdef import GodThreads


def parse_body(body: bytes) -> GodThreads:
    res_json = parse_json(body)
    if code := res_json['no']:
        raise TiebaServerError(code, res_json['error'])

    god_threads = GodThreads.from_tbdata(res_json)

    return god_threads


async def request(http_core: HttpCore, pn: int, rn: int) -> GodThreads:
    params = [
        ('pn', pn),
        ('rn', rn),
    ]

    request = http_core.pack_web_get_request(
        yarl.URL.build(scheme="https", host=WEB_BASE_HOST, path="/mo/q/activity/getActivityThreadList"), params
    )

    body = await http_core.net_core.send_request(request, read_bufsize=128 * 1024)
    return parse_body(body)
