import yarl

from .._core import HttpCore
from .._helper import pack_web_get_request, parse_json, send_request
from ..const import WEB_BASE_HOST
from ..exception import TiebaServerError, TiebaValueError


def parse_body(body: bytes) -> int:
    res_json = parse_json(body)
    if code := res_json['no']:
        raise TiebaServerError(code, res_json['error'])

    if not (fid := res_json['data']['fid']):
        raise TiebaValueError("fid is 0")

    return fid


async def request(http_core: HttpCore, fname: str) -> int:
    params = [
        ('fname', fname),
        ('ie', 'utf-8'),
    ]

    request = pack_web_get_request(
        http_core,
        yarl.URL.build(scheme="http", host=WEB_BASE_HOST, path="/f/commit/share/fnameShareApi"),
        params,
    )

    __log__ = "fname={fname}"  # noqa: F841

    body = await send_request(request, http_core.connector, read_bufsize=2 * 1024)
    return parse_body(body)
