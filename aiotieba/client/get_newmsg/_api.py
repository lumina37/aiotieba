from typing import Dict

import httpx

from .._classdef.core import TiebaCore
from .._exception import TiebaServerError
from .._helper import APP_BASE_HOST, pack_form_request, parse_json, raise_for_status, sign, url


def pack_request(client: httpx.AsyncClient, core: TiebaCore) -> httpx.Request:

    data = [('BDUSS', core.BDUSS)]

    request = pack_form_request(
        client,
        url("http", APP_BASE_HOST, "/c/s/msg"),
        sign(data),
    )

    return request


def parse_response(response: httpx.Response) -> Dict[str, bool]:
    raise_for_status(response)

    res_json = parse_json(response.content)
    if code := int(res_json['error_code']):
        raise TiebaServerError(code, res_json['error_msg'])

    msg = {k: bool(int(v)) for k, v in res_json['message'].items()}

    return msg
