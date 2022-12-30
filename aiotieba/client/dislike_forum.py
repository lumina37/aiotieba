import httpx

from .._exception import TiebaServerError
from .common.helper import jsonlib, pack_form_request, sign, timestamp_ms


def pack_request(client: httpx.AsyncClient, bduss: str, version: str, fid: int) -> httpx.Request:

    data = [
        ('BDUSS', bduss),
        ('_client_version', version),
        (
            'dislike',
            jsonlib.dumps([{"tid": 1, "dislike_ids": 7, "fid": fid, "click_time": timestamp_ms()}]),
        ),
        ('dislike_from', "homepage"),
    ]

    request = pack_form_request(client, "http://tiebac.baidu.com/c/c/excellent/submitDislike", sign(data))

    return request


def parse_response(response: httpx.Response) -> None:
    response.raise_for_status()

    res_json = jsonlib.loads(response.content)
    if code := int(res_json['error_code']):
        raise TiebaServerError(code, res_json['error_msg'])
