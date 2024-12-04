import yarl

from ...const import WEB_BASE_HOST
from ...core import HttpCore
from ...exception import TiebaServerError
from ...helper import parse_json
from ._classdef import RecoverThread


def parse_body(body: bytes) -> RecoverThread:
    res_json = parse_json(body)
    if code := res_json['no']:
        raise TiebaServerError(code, res_json['error'])

    data_map = res_json['data']
    rec_thread = RecoverThread.from_tbdata(data_map)

    return rec_thread


async def request(http_core: HttpCore, fid: int, tid: int) -> RecoverThread:
    params = [
        ('forum_id', fid),
        ('thread_id', tid),
        ('type', 1),
        ('sub_type', 1),
    ]

    request = http_core.pack_web_get_request(
        yarl.URL.build(scheme="https", host=WEB_BASE_HOST, path="/mo/q/bawu/getRecoverInfo"), params
    )

    body = await http_core.net_core.send_request(request, read_bufsize=16 * 1024)
    return parse_body(body)
