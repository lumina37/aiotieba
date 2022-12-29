from typing import List

import httpx

from .._exception import TiebaServerError
from .common.helper import jsonlib, pack_form_request, sign


def pack_request(
    client: httpx.AsyncClient, bduss: str, tbs: str, fid: int, tids: List[int], block: bool
) -> httpx.Request:

    data = [
        ('BDUSS', bduss),
        ('forum_id', fid),
        ('tbs', tbs),
        ('thread_ids', ','.join([str(tid) for tid in tids])),
        ('type', '2' if block else '1'),
    ]

    request = pack_form_request(client, "http://tiebac.baidu.com/c/c/bawu/multiDelThread", sign(data))

    return request


def parse_response(response: httpx.Response) -> None:
    response.raise_for_status()

    res_json = jsonlib.loads(response.content)
    if code := int(res_json['error_code']):
        raise TiebaServerError(code, res_json['error_msg'])
