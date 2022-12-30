import httpx

from .._exception import TiebaServerError
from .common.helper import jsonlib, pack_form_request, sign
from .common.typedef import Follows


def pack_request(client: httpx.AsyncClient, bduss: str, version: str, user_id: int, pn: int) -> httpx.Request:

    data = [
        ('BDUSS', bduss),
        ('_client_version', version),
        ('pn', pn),
        ('uid', user_id),
    ]

    request = pack_form_request(client, "http://tiebac.baidu.com/c/u/follow/followList", sign(data))

    return request


def parse_response(response: httpx.Response) -> Follows:
    response.raise_for_status()

    res_json = jsonlib.loads(response.content)
    if code := int(res_json['error_code']):
        raise TiebaServerError(code, res_json['error_msg'])

    follows = Follows(res_json)

    return follows
