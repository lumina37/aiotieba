from typing import Dict

import httpx

from .._exception import TiebaServerError
from .common.helper import jsonlib, pack_form_request, sign


def pack_request(client: httpx.AsyncClient, bduss: str) -> httpx.Request:

    data = [
        ('BDUSS', bduss),
    ]

    request = pack_form_request(client, "http://tiebac.baidu.com/c/s/msg", sign(data))

    return request


def parse_response(response: httpx.Response) -> Dict[str, bool]:
    response.raise_for_status()

    res_json = jsonlib.loads(response.content)
    if code := int(res_json['error_code']):
        raise TiebaServerError(code, res_json['error_msg'])

    msg = {k: bool(int(v)) for k, v in res_json['message'].items()}

    return msg
