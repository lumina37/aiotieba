import sys

import yarl

from .._core import APP_BASE_HOST, HttpCore
from .._helper import APP_SECURE_SCHEME, log_exception, log_success, pack_form_request, parse_json, send_request
from ..exception import TiebaServerError


def parse_body(body: bytes) -> None:
    res_json = parse_json(body)
    if code := int(res_json['error_code']):
        raise TiebaServerError(code, res_json['error_msg'])
    if code := int(res_json['data']['is_push_success']) != 1:
        raise TiebaServerError(code, res_json['data']['msg'])


async def request(http_core: HttpCore, fid: int, tid: int) -> bool:

    data = [
        ('BDUSS', http_core.core._BDUSS),
        ('forum_id', fid),
        ('thread_id', tid),
    ]

    request = pack_form_request(
        http_core,
        yarl.URL.build(scheme=APP_SECURE_SCHEME, host=APP_BASE_HOST, path="/c/c/bawu/pushRecomToPersonalized"),
        data,
    )

    log_str = f"fid={fid} tid={tid}"
    frame = sys._getframe(1)

    try:
        body = await send_request(request, http_core.connector, read_bufsize=2 * 1024)
        parse_body(body)

    except Exception as err:
        log_exception(frame, err, log_str)
        return False

    log_success(frame, log_str)
    return True
