import httpx

from .._exception import TiebaServerError
from .common.helper import jsonlib, pack_form_request, sign


def pack_request(
    client: httpx.AsyncClient,
    bduss: str,
    tbs: str,
    version: str,
    cuid_galaxy2: str,
    tid: int,
    pid: int,
    is_disagree: bool,
    is_undo: bool,
) -> httpx.Request:

    data = [
        ('BDUSS', bduss),
        ('_client_version', version),
        ('agree_type', '5' if is_disagree else '2'),
        ('cuid', cuid_galaxy2),
        ('obj_type', '1' if pid else '3'),
        ('op_type', int(is_undo)),
        ('post_id', pid),
        ('tbs', tbs),
        ('thread_id', tid),
    ]

    request = pack_form_request(client, "http://tiebac.baidu.com/c/c/agree/opAgree", sign(data))

    return request


def parse_response(response: httpx.Response) -> None:
    response.raise_for_status()

    res_json = jsonlib.loads(response.content)
    if code := int(res_json['error_code']):
        raise TiebaServerError(code, res_json['error_msg'])
