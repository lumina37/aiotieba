import aiohttp
import yarl

from .._core import APP_BASE_HOST, APP_SECURE_SCHEME, TbCore
from .._exception import TiebaServerError
from .._helper import pack_form_request, parse_json, send_request


async def request(connector: aiohttp.TCPConnector, core: TbCore, tbs: str, fname: str) -> bytes:

    data = [
        ('BDUSS', core._BDUSS),
        ('_client_version', core.main_version),
        ('kw', fname),
        ('tbs', tbs),
    ]

    request = pack_form_request(
        core,
        yarl.URL.build(scheme=APP_SECURE_SCHEME, host=APP_BASE_HOST, path="/c/c/forum/sign"),
        data,
    )

    body = await send_request(request, connector, read_bufsize=2 * 1024)

    return body


def parse_body(body: bytes) -> None:
    res_json = parse_json(body)
    if code := int(res_json['error_code']):
        raise TiebaServerError(code, res_json['error_msg'])
    if int(res_json['user_info']['sign_bonus_point']) == 0:
        raise TiebaServerError(-1, "sign_bonus_point is 0")
