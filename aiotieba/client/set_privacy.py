import httpx

from .._exception import TiebaServerError
from .common.core import TiebaCore
from .common.helper import APP_BASE_HOST, jsonlib, pack_form_request, raise_for_status, sign, url


def pack_request(client: httpx.AsyncClient, core: TiebaCore, fid: int, tid: int, pid: int, hide: bool) -> httpx.Request:

    data = [
        ('BDUSS', core.BDUSS),
        ('forum_id', fid),
        ('is_hide', str(int(hide))),
        ('post_id', pid),
        ('thread_id', tid),
    ]

    request = pack_form_request(
        client,
        url("http", APP_BASE_HOST, "/c/c/thread/setPrivacy"),
        sign(data),
    )

    return request


def parse_response(response: httpx.Response) -> None:
    raise_for_status(response)

    res_json = jsonlib.loads(response.content)
    if code := int(res_json['error_code']):
        raise TiebaServerError(code, res_json['error_msg'])
