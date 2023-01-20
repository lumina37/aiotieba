import aiohttp
import yarl

from .._core import APP_BASE_HOST, TbCore
from .._exception import TiebaServerError
from .._helper import APP_SECURE_SCHEME, pack_form_request, parse_json, send_request


async def request(
    connector: aiohttp.TCPConnector, core: TbCore, tbs: str, fname: str, fid: int, portrait: str, day: int, reason: str
) -> bytes:

    data = [
        ('BDUSS', core._BDUSS),
        ('day', day),
        ('fid', fid),
        ('ntn', 'banid'),
        ('portrait', portrait),
        ('reason', reason),
        ('tbs', tbs),
        ('word', fname),
        ('z', '6'),
    ]

    request = pack_form_request(
        core,
        yarl.URL.build(scheme=APP_SECURE_SCHEME, host=APP_BASE_HOST, path="/c/c/bawu/commitprison"),
        data,
    )

    body = await send_request(request, connector, read_bufsize=1024)

    return body


def parse_body(body: bytes) -> None:
    res_json = parse_json(body)
    if code := int(res_json['error_code']):
        raise TiebaServerError(code, res_json['error_msg'])
