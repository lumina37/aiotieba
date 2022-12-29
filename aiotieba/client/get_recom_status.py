from typing import Tuple

import httpx

from .._exception import TiebaServerError
from .common.helper import jsonlib, pack_form_request, sign


def pack_request(client: httpx.AsyncClient, bduss: str, version: str, fid: int) -> httpx.Request:

    data = [
        ('BDUSS', bduss),
        ('_client_version', version),
        ('forum_id', fid),
        ('pn', '1'),
        ('rn', '0'),
    ]

    request = pack_form_request(client, "http://tiebac.baidu.com/c/f/bawu/getRecomThreadList", sign(data))

    return request


def parse_response(response: httpx.Response) -> Tuple[int, int]:
    response.raise_for_status()

    res_json = jsonlib.loads(response.content)
    if code := int(res_json['error_code']):
        raise TiebaServerError(code, res_json['error_msg'])

    total_recom_num = int(res_json['total_recommend_num'])
    used_recom_num = int(res_json['used_recommend_num'])

    return total_recom_num, used_recom_num
