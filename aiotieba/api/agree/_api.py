import yarl

from ...const import APP_BASE_HOST, APP_SECURE_SCHEME, MAIN_VERSION
from ...core import HttpCore
from ...exception import BoolResponse, TiebaServerError
from ...helper import parse_json


def parse_body(body: bytes) -> None:
    res_json = parse_json(body)
    if code := int(res_json['error_code']):
        raise TiebaServerError(code, res_json['error_msg'])


async def request(
    http_core: HttpCore, tid: int, pid: int, is_comment: bool, is_disagree: bool, is_undo: bool
) -> BoolResponse:
    if pid:
        obj_type = 2 if is_comment else 1
    else:
        obj_type = 3

    data = [
        ('BDUSS', http_core.account.BDUSS),
        ('_client_version', MAIN_VERSION),
        ('agree_type', 5 if is_disagree else 2),
        ('cuid', http_core.account.cuid_galaxy2),
        ('obj_type', obj_type),
        ('op_type', str(int(is_undo))),
        ('post_id', pid),
        ('tbs', http_core.account.tbs),
        ('thread_id', tid),
    ]

    request = http_core.pack_form_request(
        yarl.URL.build(scheme=APP_SECURE_SCHEME, host=APP_BASE_HOST, path="/c/c/agree/opAgree"), data
    )

    body = await http_core.net_core.send_request(request, read_bufsize=1024)
    parse_body(body)

    return BoolResponse()
