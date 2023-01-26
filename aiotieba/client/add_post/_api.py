import sys
import time

import aiohttp
import yarl

from .._core import APP_BASE_HOST, TbCore
from .._exception import TiebaServerError, TiebaValueError
from .._helper import APP_SECURE_SCHEME, log_exception, log_success, pack_form_request, parse_json, send_request


def parse_body(body: bytes) -> None:
    res_json = parse_json(body)
    if code := int(res_json['error_code']):
        raise TiebaServerError(code, res_json['error_msg'])
    if int(res_json['info']['need_vcode']):
        raise TiebaValueError("need verify code")


async def request(connector: aiohttp.TCPConnector, core: TbCore, fname: str, fid: int, tid: int, content: str) -> bool:

    data = [
        ('BDUSS', core._BDUSS),
        ('_client_id', core._client_id),
        ('_client_type', '2'),
        ('_client_version', core.post_version),
        ('_phone_imei', '000000000000000'),
        ('anonymous', '1'),
        ('barrage_time', '0'),
        ('can_no_forum', '0'),
        ('content', content),
        ('cuid', core.cuid),
        ('cuid_galaxy2', core.cuid_galaxy2),
        ('cuid_gid', ''),
        ('fid', fid),
        ('from', '1021099l'),
        ('from_forum_id', 'null'),
        ('is_ad', '0'),
        ('is_barrage', '0'),
        ('is_feedback', '0'),
        ('kw', fname),
        ('model', 'M2012K11AC'),
        ('net_type', '1'),
        ('new_vcode', '1'),
        ('post_from', '3'),
        ('reply_uid', 'null'),
        ('stoken', core._STOKEN),
        ('subapp_type', 'mini'),
        ('tbs', core._tbs),
        ('tid', tid),
        ('timestamp', int(time.time() * 1000)),
        ('v_fid', ''),
        ('v_fname', ''),
        ('vcode_tag', '12'),
        ('z_id', core.z_id),
    ]

    request = pack_form_request(
        core,
        yarl.URL.build(scheme=APP_SECURE_SCHEME, host=APP_BASE_HOST, path="/c/c/post/add"),
        data,
    )

    log_str = f"fname={fname} tid={tid}"
    frame = sys._getframe(1)

    try:
        body = await send_request(request, connector, read_bufsize=2 * 1024)
        parse_body(body)

    except Exception as err:
        log_exception(frame, err, log_str)
        return False

    log_success(frame, log_str)
    return True
