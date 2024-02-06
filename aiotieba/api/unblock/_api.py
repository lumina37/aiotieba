import yarl

from ...const import WEB_BASE_HOST
from ...core import HttpCore
from ...exception import BoolResponse, TiebaServerError
from ...helper import parse_json


def parse_body(body: bytes) -> None:
    res_json = parse_json(body)
    if code := res_json['no']:
        raise TiebaServerError(code, res_json['error'])


async def request(http_core: HttpCore, fid: int, user_id: int) -> BoolResponse:
    data = [
        ('fn', '-'),
        ('fid', fid),
        ('block_un', '-'),
        ('block_uid', user_id),
        ('tbs', http_core.account.tbs),
    ]

    request = http_core.pack_web_form_request(
        yarl.URL.build(scheme="https", host=WEB_BASE_HOST, path="/mo/q/bawublockclear"), data
    )

    body = await http_core.net_core.send_request(request, read_bufsize=1024)
    parse_body(body)

    return BoolResponse()
