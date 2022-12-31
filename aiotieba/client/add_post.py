import time

import httpx

from .._exception import TiebaServerError
from .common.core import TiebaCore
from .common.helper import APP_BASE_HOST, jsonlib, pack_form_request, raise_for_status, sign, url


def pack_request(
    client: httpx.AsyncClient, core: TiebaCore, tbs: str, fname: str, fid: int, tid: int, content: str
) -> httpx.Request:

    data = [
        ('BDUSS', core.BDUSS),
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
        ('stoken', core.STOKEN),
        ('subapp_type', 'mini'),
        ('tbs', tbs),
        ('tid', tid),
        ('timestamp', int(time.time() * 1000)),
        ('v_fid', ''),
        ('v_fname', ''),
        ('vcode_tag', '12'),
    ]

    request = pack_form_request(
        client,
        url("http", APP_BASE_HOST, "/c/c/post/add"),
        sign(data),
    )

    return request


def parse_response(response: httpx.Response) -> None:
    raise_for_status(response)

    res_json = jsonlib.loads(response.content)
    if code := int(res_json['error_code']):
        raise TiebaServerError(code, res_json['error_msg'])
    if int(res_json['info']['need_vcode']):
        raise TiebaServerError(-1, "need verify code")
