from typing import Dict, List

import httpx

from .._exception import TiebaServerError
from .common.core import TiebaCore
from .common.helper import APP_BASE_HOST, jsonlib, pack_form_request, raise_for_status, sign, url


def pack_request(client: httpx.AsyncClient, core: TiebaCore, fid: int) -> httpx.Request:

    data = [
        ('BDUSS', core.BDUSS),
        ('_client_version', core.main_version),
        ('forum_id', fid),
    ]
    request = pack_form_request(
        client,
        url("http", APP_BASE_HOST, "/c/f/forum/getforumdata"),
        sign(data),
    )

    return request


field_names = [
    'view',
    'thread',
    'new_member',
    'post',
    'sign_ratio',
    'average_time',
    'average_times',
    'recommend',
]


def parse_response(response: httpx.Response) -> Dict[str, List[int]]:
    raise_for_status(response)

    res_json = jsonlib.loads(response.content)
    if code := int(res_json['error_code']):
        raise TiebaServerError(code, res_json['error_msg'])

    data = res_json['data']
    stat = {
        field_name: [int(item['value']) for item in reversed(data_i['group'][1]['values'])]
        for field_name, data_i in zip(field_names, data)
    }

    return stat
