import sys
from typing import Dict, List

import aiohttp
import yarl

from .._core import APP_BASE_HOST, TbCore
from .._exception import TiebaServerError
from .._helper import APP_SECURE_SCHEME, log_exception, pack_form_request, parse_json, send_request

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


def parse_body(body: bytes) -> Dict[str, List[int]]:
    res_json = parse_json(body)
    if code := int(res_json['error_code']):
        raise TiebaServerError(code, res_json['error_msg'])

    data = res_json['data']
    stat = {
        field_name: [int(item['value']) for item in reversed(data_i['group'][1]['values'])]
        for field_name, data_i in zip(field_names, data)
    }

    return stat


async def request(connector: aiohttp.TCPConnector, core: TbCore, fid: int) -> Dict[str, List[int]]:

    data = [
        ('BDUSS', core._BDUSS),
        ('_client_version', core.main_version),
        ('forum_id', fid),
    ]

    request = pack_form_request(
        core,
        yarl.URL.build(scheme=APP_SECURE_SCHEME, host=APP_BASE_HOST, path="/c/f/forum/getforumdata"),
        data,
    )

    try:
        body = await send_request(request, connector, read_bufsize=4 * 1024)
        stat = parse_body(body)

    except Exception as err:
        log_exception(sys._getframe(1), err, f"fid={fid}")
        stat = {field_name: [] for field_name in field_names}

    return stat
