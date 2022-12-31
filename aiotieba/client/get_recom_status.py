from typing import Tuple

import httpx

from .._exception import TiebaServerError
from .common.core import TiebaCore
from .common.helper import APP_BASE_HOST, jsonlib, pack_form_request, raise_for_status, sign, url


def pack_request(client: httpx.AsyncClient, core: TiebaCore, fid: int) -> httpx.Request:

    data = [
        ('BDUSS', core.BDUSS),
        ('_client_version', core.main_version),
        ('forum_id', fid),
        ('pn', '1'),
        ('rn', '0'),
    ]

    request = pack_form_request(
        client,
        url("http", APP_BASE_HOST, "/c/f/bawu/getRecomThreadList"),
        sign(data),
    )

    return request


def parse_response(response: httpx.Response) -> Tuple[int, int]:
    raise_for_status(response)

    res_json = jsonlib.loads(response.content)
    if code := int(res_json['error_code']):
        raise TiebaServerError(code, res_json['error_msg'])

    total_recom_num = int(res_json['total_recommend_num'])
    used_recom_num = int(res_json['used_recommend_num'])

    return total_recom_num, used_recom_num
