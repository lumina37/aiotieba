import yarl

from ...const import WEB_BASE_HOST
from ...core import HttpCore
from ...exception import BoolResponse, TiebaServerError
from ...helper import parse_json


def parse_body(body: bytes) -> None:
    res_json = parse_json(body)
    if code := res_json['errno']:
        raise TiebaServerError(code, res_json['errmsg'])


async def request(http_core: HttpCore, fname: str, user_id: int) -> BoolResponse:
    data = [
        ('word', fname),
        ('tbs', http_core.account.tbs),
        ('list[]', user_id),
        ('ie', 'utf-8'),
    ]

    request = http_core.pack_web_form_request(
        yarl.URL.build(scheme="http", host=WEB_BASE_HOST, path="/bawu2/platform/cancelBlack"), data
    )

    body = await http_core.net_core.send_request(request, read_bufsize=2 * 1024)
    parse_body(body)

    return BoolResponse()
