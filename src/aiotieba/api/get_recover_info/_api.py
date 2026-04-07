import yarl

from ...const import WEB_BASE_HOST
from ...core import HttpCore
from ...exception import TiebaServerError
from ...helper import parse_json
from ._classdef import RecoverInfo


def parse_body(body: bytes) -> RecoverInfo:
    res_json = parse_json(body)
    if code := res_json["no"]:
        raise TiebaServerError(code, res_json["error"])

    data_map = res_json["data"]
    rec_info = RecoverInfo.from_tbdata(data_map)

    return rec_info


async def request(http_core: HttpCore, fid: int, tid: int, pid: int) -> RecoverInfo:
    params = [
        ("forum_id", fid),
        ("thread_id", tid),
        ("post_id", pid),
        ("type", 1),
        ("sub_type", 2 if pid else 1),
    ]

    request = http_core.pack_web_get_request(
        yarl.URL.build(scheme="https", host=WEB_BASE_HOST, path="/mo/q/bawu/getRecoverInfo"), params
    )

    body = await http_core.net_core.send_request(request, read_bufsize=16 * 1024)
    return parse_body(body)
