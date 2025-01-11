import yarl

from ...const import MAIN_VERSION, WEB_BASE_HOST
from ...core import HttpCore
from ...exception import BoolResponse, TiebaServerError
from ...helper import parse_json


def parse_body(body: bytes) -> None:
    res_json = parse_json(body)
    if code := int(res_json["error_code"]):
        raise TiebaServerError(code, res_json["error_msg"])
    if code := int(res_json["error"]["errno"]):
        raise TiebaServerError(code, res_json["error"]["errmsg"])


async def request(http_core: HttpCore) -> BoolResponse:
    data = [
        ("_client_version", MAIN_VERSION),
        ("subapp_type", "hybrid"),
    ]

    request = http_core.pack_web_form_request(
        yarl.URL.build(scheme="https", host=WEB_BASE_HOST, path="/c/c/forum/msign"),
        data,
        extra_headers=[("Subapp-Type", "hybrid")],
    )

    body = await http_core.net_core.send_request(request, read_bufsize=2 * 1024)
    parse_body(body)

    return BoolResponse()
