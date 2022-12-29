import httpx

from .._exception import TiebaServerError
from .common.helper import jsonlib, pack_form_request, sign
from .common.typedef import RecomThreads


def pack_request(client: httpx.AsyncClient, bduss: str, version: str, fid: int, pn: int, rn: int) -> httpx.Request:

    data = [
        ('BDUSS', bduss),
        ('_client_version', version),
        ('forum_id', fid),
        ('pn', pn),
        ('rn', rn),
    ]

    request = pack_form_request(client, "http://tiebac.baidu.com/c/f/bawu/getRecomThreadHistory", sign(data))

    return request


def parse_response(response: httpx.Response) -> RecomThreads:
    response.raise_for_status()

    res_json = jsonlib.loads(response.content)
    if code := int(res_json['error_code']):
        raise TiebaServerError(code, res_json['error_msg'])

    recom_threads = RecomThreads(res_json)

    return recom_threads
