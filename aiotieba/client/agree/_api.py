import sys

import yarl

from .._core import HttpCore
from .._helper import log_success, pack_form_request, parse_json, send_request
from ..const import APP_BASE_HOST, APP_SECURE_SCHEME
from ..exception import TiebaServerError


def parse_body(body: bytes) -> None:
    res_json = parse_json(body)
    if code := int(res_json['error_code']):
        raise TiebaServerError(code, res_json['error_msg'])


async def request(http_core: HttpCore, tid: int, pid: int, is_disagree: bool, is_undo: bool) -> bool:
    data = [
        ('BDUSS', http_core.core._BDUSS),
        ('_client_version', http_core.core.main_version),
        ('agree_type', '5' if is_disagree else '2'),
        ('cuid', http_core.core.cuid_galaxy2),
        ('obj_type', '1' if pid else '3'),
        ('op_type', str(int(is_undo))),
        ('post_id', pid),
        ('tbs', http_core.core._tbs),
        ('thread_id', tid),
    ]

    request = pack_form_request(
        http_core,
        yarl.URL.build(scheme=APP_SECURE_SCHEME, host=APP_BASE_HOST, path="/c/c/agree/opAgree"),
        data,
    )

    __log__ = f"tid={tid} pid={pid}"

    body = await send_request(request, http_core.connector, read_bufsize=1024)
    parse_body(body)

    log_success(sys._getframe(1), __log__)
    return True
