import time

import aiohttp
import yarl

from .._core import APP_BASE_HOST, TbCore
from .._exception import TiebaServerError
from .._helper import APP_SECURE_SCHEME, pack_form_request, parse_json, send_request


async def request(
    connector: aiohttp.TCPConnector, core: TbCore, tbs: str, fname: str, fid: int, tid: int, content: str
) -> bytes:

    data = [
        ('BDUSS', core._BDUSS),
        ('_client_id', core.client_id),
        ('_client_type', '2'),
        ('_client_version', core.post_version),
        ('_phone_imei', '000000000000000'),
        ('anonymous', '1'),
        ('apid', 'sw'),
        ('content', content),
        ('cuid', core.cuid),
        ('cuid_galaxy2', core.cuid_galaxy2),
        ('cuid_gid', ''),
        ('fid', fid),
        ('kw', fname),
        ('model', 'M2012K11AC'),
        ('net_type', '1'),
        ('new_vcode', '1'),
        ('post_from', '3'),
        ('reply_uid', 'null'),
        ('stoken', core._STOKEN),
        ('subapp_type', 'mini'),
        ('tbs', tbs),
        ('tid', tid),
        ('timestamp', int(time.time() * 1000)),
        ('v_fid', ''),
        ('v_fname', ''),
        ('vcode_tag', '12'),
    ]

    request = pack_form_request(
        core,
        yarl.URL.build(scheme=APP_SECURE_SCHEME, host=APP_BASE_HOST, path="/c/c/post/add"),
        data,
    )

    body = await send_request(request, connector, read_bufsize=2 * 1024)

    return body


def parse_body(body: bytes) -> None:
    res_json = parse_json(body)
    if code := int(res_json['error_code']):
        raise TiebaServerError(code, res_json['error_msg'])
    if int(res_json['info']['need_vcode']):
        raise TiebaServerError(-1, "need verify code")
