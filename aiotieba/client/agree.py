import httpx

from .._exception import TiebaServerError
from .common.core import TiebaCore
from .common.helper import APP_BASE_HOST, jsonlib, pack_form_request, raise_for_status, sign, url


def pack_request(
    client: httpx.AsyncClient, core: TiebaCore, tbs: str, tid: int, pid: int, is_disagree: bool, is_undo: bool
) -> httpx.Request:

    data = [
        ('BDUSS', core.BDUSS),
        ('_client_version', core.main_version),
        ('agree_type', '5' if is_disagree else '2'),
        ('cuid', core.cuid_galaxy2),
        ('obj_type', '1' if pid else '3'),
        ('op_type', str(int(is_undo))),
        ('post_id', pid),
        ('tbs', tbs),
        ('thread_id', tid),
    ]

    request = pack_form_request(
        client,
        url("http", APP_BASE_HOST, "/c/c/agree/opAgree"),
        sign(data),
    )

    return request


def parse_response(response: httpx.Response) -> None:
    raise_for_status(response)

    res_json = jsonlib.loads(response.content)
    if code := int(res_json['error_code']):
        raise TiebaServerError(code, res_json['error_msg'])
