import sys

import aiohttp
import yarl

from .._core import APP_BASE_HOST, WEB_BASE_HOST, TbCore
from .._exception import TiebaServerError
from .._helper import (
    APP_SECURE_SCHEME,
    log_exception,
    log_success,
    pack_form_request,
    pack_web_form_request,
    parse_json,
    send_request,
)


def parse_body_app(body: bytes) -> None:
    res_json = parse_json(body)
    if code := int(res_json['error_code']):
        raise TiebaServerError(code, res_json['error_msg'])


async def request_app(connector: aiohttp.TCPConnector, core: TbCore, act_type: str) -> bool:

    data = [
        ('BDUSS', core._BDUSS),
        ('act_type', act_type),
        ('cuid', ' '),
        ('tbs', core._tbs),
    ]

    request = pack_form_request(
        core,
        yarl.URL.build(scheme=APP_SECURE_SCHEME, host=APP_BASE_HOST, path="/c/c/user/commitUGTaskInfo"),
        data,
    )

    frame = sys._getframe(1)

    try:
        body = await send_request(request, connector, read_bufsize=1024)
        parse_body_app(body)

    except Exception as err:
        log_exception(frame, err)
        return False

    log_success(frame)
    return True


def parse_body_web(body: bytes) -> None:
    res_json = parse_json(body)
    if code := res_json['no']:
        raise TiebaServerError(code, res_json['error'])


async def request_web(connector: aiohttp.TCPConnector, core: TbCore, act_type: str) -> bool:

    data = [
        ('tbs', core._tbs),
        ('act_type', act_type),
        ('cuid', ' '),
    ]

    request = pack_web_form_request(
        core,
        yarl.URL.build(scheme="https", host=WEB_BASE_HOST, path="/mo/q/usergrowth/commitUGTaskInfo"),
        data,
    )

    frame = sys._getframe(1)

    try:
        body = await send_request(request, connector, read_bufsize=1024)
        parse_body_web(body)

    except Exception as err:
        log_exception(frame, err)
        return False

    log_success(frame)
    return True
