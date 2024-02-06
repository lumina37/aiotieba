import yarl

from ...const import WEB_BASE_HOST
from ...core import HttpCore
from ...exception import BoolResponse, TiebaServerError
from ...helper import parse_json


def parse_body(body: bytes) -> None:
    res_json = parse_json(body)
    if code := res_json['no']:
        raise TiebaServerError(code, res_json['error'])


async def request(http_core: HttpCore, fid: int, tid: int, pid: int, is_hide: bool) -> BoolResponse:
    data = [
        ('tbs', http_core.account.tbs),
        ('fn', '-'),
        ('fid', fid),
        ('tid_list[]', tid),
        ('pid_list[]', pid),
        ('type_list[]', 1 if pid else 0),
        ('is_frs_mask_list[]', int(is_hide)),
    ]

    request = http_core.pack_web_form_request(
        yarl.URL.build(scheme="https", host=WEB_BASE_HOST, path="/mo/q/bawurecoverthread"), data
    )

    body = await http_core.net_core.send_request(request, read_bufsize=1024)
    parse_body(body)

    return BoolResponse()
