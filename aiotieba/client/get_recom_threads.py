import httpx

from .._exception import TiebaServerError
from .common.core import TiebaCore
from .common.helper import APP_BASE_HOST, jsonlib, pack_form_request, raise_for_status, sign, url
from .common.typedef import RecomThreads


def pack_request(client: httpx.AsyncClient, core: TiebaCore, fid: int, pn: int, rn: int) -> httpx.Request:

    data = [
        ('BDUSS', core.BDUSS),
        ('_client_version', core.main_version),
        ('forum_id', fid),
        ('pn', pn),
        ('rn', rn),
    ]

    request = pack_form_request(
        client,
        url("http", APP_BASE_HOST, "/c/f/bawu/getRecomThreadHistory"),
        sign(data),
    )

    return request


def parse_response(response: httpx.Response) -> RecomThreads:
    raise_for_status(response)

    res_json = jsonlib.loads(response.content)
    if code := int(res_json['error_code']):
        raise TiebaServerError(code, res_json['error_msg'])

    recom_threads = RecomThreads(res_json)

    return recom_threads
