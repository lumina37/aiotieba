import sys

import aiohttp
import yarl

from .._core import WEB_BASE_HOST, TbCore
from .._exception import TiebaServerError
from .._helper import log_exception, log_success, pack_web_form_request, parse_json, send_request


def parse_body(body: bytes) -> None:
    res_json = parse_json(body)
    if code := res_json['errno']:
        raise TiebaServerError(code, res_json['errmsg'])


async def request(connector: aiohttp.TCPConnector, core: TbCore, fname: str, user_id: int) -> bool:

    data = [
        ('tbs', core._tbs),
        ('user_id', user_id),
        ('word', fname),
        ('ie', 'utf-8'),
    ]

    request = pack_web_form_request(
        core,
        yarl.URL.build(scheme="http", host=WEB_BASE_HOST, path="/bawu2/platform/addBlack"),
        data,
    )

    log_str = f"fname={fname} user_id={user_id}"
    frame = sys._getframe(1)

    try:
        body = await send_request(request, connector, read_bufsize=2 * 1024)
        parse_body(body)

    except Exception as err:
        log_exception(frame, err, log_str)
        return False

    log_success(frame, log_str)
    return True
