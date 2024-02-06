import yarl

from ...const import APP_BASE_HOST, APP_SECURE_SCHEME
from ...core import HttpCore
from ...exception import BoolResponse, TiebaServerError
from ...helper import parse_json


def parse_body(body: bytes) -> None:
    res_json = parse_json(body)
    if code := int(res_json['error_code']):
        raise TiebaServerError(code, res_json['error_msg'])


async def request(http_core: HttpCore, fid: int, tid: int, pid: int, is_hide: bool) -> BoolResponse:
    data = [
        ('BDUSS', http_core.account.BDUSS),
        ('forum_id', fid),
        ('is_hide', str(int(is_hide))),
        ('post_id', pid),
        ('thread_id', tid),
    ]

    request = http_core.pack_form_request(
        yarl.URL.build(scheme=APP_SECURE_SCHEME, host=APP_BASE_HOST, path="/c/c/thread/setPrivacy"), data
    )

    body = await http_core.net_core.send_request(request, read_bufsize=1024)
    parse_body(body)

    return BoolResponse()
