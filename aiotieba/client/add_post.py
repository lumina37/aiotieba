import httpx

from .._exception import TiebaServerError
from .common.helper import jsonlib, pack_form_request, sign, timestamp_ms


def pack_request(
    client: httpx.AsyncClient,
    bduss: str,
    stoken: str,
    tbs: str,
    version: str,
    cuid: str,
    cuid_galaxy2: str,
    client_id: str,
    fname: str,
    fid: int,
    tid: int,
    content: str,
) -> httpx.Request:

    data = [
        ('BDUSS', bduss),
        ('_client_id', client_id),
        ('_client_type', '2'),
        ('_client_version', version),
        ('_phone_imei', '000000000000000'),
        ('anonymous', '1'),
        ('apid', 'sw'),
        ('content', content),
        ('cuid', cuid),
        ('cuid_galaxy2', cuid_galaxy2),
        ('cuid_gid', ''),
        ('fid', fid),
        ('kw', fname),
        ('model', 'M2012K11AC'),
        ('net_type', '1'),
        ('new_vcode', '1'),
        ('post_from', '3'),
        ('reply_uid', 'null'),
        ('stoken', stoken),
        ('subapp_type', 'mini'),
        ('tbs', tbs),
        ('tid', tid),
        ('timestamp', timestamp_ms()),
        ('v_fid', ''),
        ('v_fname', ''),
        ('vcode_tag', '12'),
    ]

    request = pack_form_request(client, "http://tiebac.baidu.com/c/c/post/add", sign(data))

    return request


def parse_response(response: httpx.Response) -> None:
    response.raise_for_status()

    res_json = jsonlib.loads(response.content)
    if code := int(res_json['error_code']):
        raise TiebaServerError(code, res_json['error_msg'])
    if int(res_json['info']['need_vcode']):
        raise TiebaServerError(-1, "need verify code")
