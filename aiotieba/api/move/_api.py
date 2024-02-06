import yarl

from ...const import APP_BASE_HOST, APP_SECURE_SCHEME, MAIN_VERSION
from ...core import HttpCore
from ...exception import BoolResponse, TiebaServerError
from ...helper import pack_json, parse_json


def parse_body(body: bytes) -> None:
    res_json = parse_json(body)
    if code := int(res_json['error_code']):
        raise TiebaServerError(code, res_json['error_msg'])


async def request(http_core: HttpCore, fid: int, tid: int, to_tab_id: int, from_tab_id: int) -> BoolResponse:
    data = [
        ('BDUSS', http_core.account.BDUSS),
        ('_client_version', MAIN_VERSION),
        ('forum_id', fid),
        ('tbs', http_core.account.tbs),
        ('threads', pack_json([{"thread_id": tid, "from_tab_id": from_tab_id, "to_tab_id": to_tab_id}])),
    ]

    request = http_core.pack_form_request(
        yarl.URL.build(scheme=APP_SECURE_SCHEME, host=APP_BASE_HOST, path="/c/c/bawu/moveTabThread"), data
    )

    body = await http_core.net_core.send_request(request, read_bufsize=1024)
    parse_body(body)

    return BoolResponse()
