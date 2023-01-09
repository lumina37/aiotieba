from typing import List

import httpx

from .._exception import TiebaServerError
from .._helper import pack_form_request, parse_json, raise_for_status, url


def pack_request(
    client: httpx.AsyncClient, tbs: str, fname: str, fid: int, appeal_ids: List[int], refuse: bool
) -> httpx.Request:

    data = (
        [
            ('fn', fname),
            ('fid', fid),
        ]
        + [(f'appeal_list[{i}]', appeal_id) for i, appeal_id in enumerate(appeal_ids)]
        + [
            ('refuse_reason', '_'),
            ('status', '2' if refuse else '1'),
            ('tbs', tbs),
        ]
    )

    request = pack_form_request(
        client,
        url("https", "tieba.baidu.com", "/mo/q/multiAppealhandle"),
        data,
    )

    return request


def parse_response(response: httpx.Response) -> None:
    raise_for_status(response)

    res_json = parse_json(response.content)
    if code := res_json['no']:
        raise TiebaServerError(code, res_json['error'])
