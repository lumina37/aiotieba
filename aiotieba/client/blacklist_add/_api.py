import aiohttp
import yarl

from .._core import WEB_BASE_HOST, TbCore
from .._exception import TiebaServerError
from .._helper import pack_web_form_request, parse_json, send_request


async def request(connector: aiohttp.TCPConnector, core: TbCore, tbs: str, fname: str, user_id: int) -> bytes:

    data = [
        ('tbs', tbs),
        ('user_id', user_id),
        ('word', fname),
        ('ie', 'utf-8'),
    ]

    request = pack_web_form_request(
        core,
        yarl.URL.build(scheme="http", host=WEB_BASE_HOST, path="/bawu2/platform/addBlack"),
        data,
    )

    body = await send_request(request, connector, read_bufsize=2 * 1024)

    return body


def parse_body(body: bytes) -> None:
    res_json = parse_json(body)
    if code := res_json['errno']:
        raise TiebaServerError(code, res_json['errmsg'])
