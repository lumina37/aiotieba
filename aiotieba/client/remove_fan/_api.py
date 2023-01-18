import aiohttp
import yarl

from .._core import APP_BASE_HOST, APP_SECURE_SCHEME, TbCore
from .._exception import TiebaServerError
from .._helper import pack_form_request, parse_json, send_request


async def request(connector: aiohttp.TCPConnector, core: TbCore, tbs: str, user_id: int) -> bytes:

    data = [
        ('BDUSS', core._BDUSS),
        ('fans_uid', user_id),
        ('tbs', tbs),
    ]

    request = pack_form_request(
        core,
        yarl.URL.build(scheme=APP_SECURE_SCHEME, host=APP_BASE_HOST, path="/c/c/user/removeFans"),
        data,
    )

    body = await send_request(request, connector, read_bufsize=1024)

    return body


def parse_body(body: bytes) -> None:
    res_json = parse_json(body)
    if code := int(res_json['error_code']):
        raise TiebaServerError(code, res_json['error_msg'])
