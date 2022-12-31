import httpx

from .._exception import TiebaServerError
from .common.core import TiebaCore
from .common.helper import APP_BASE_HOST, jsonlib, pack_form_request, raise_for_status, sign, url
from .common.typedef import Follows


def pack_request(client: httpx.AsyncClient, core: TiebaCore, user_id: int, pn: int) -> httpx.Request:

    data = [
        ('BDUSS', core.BDUSS),
        ('_client_version', core.main_version),
        ('pn', pn),
        ('uid', user_id),
    ]

    request = pack_form_request(
        client,
        url("http", APP_BASE_HOST, "/c/u/follow/followList"),
        sign(data),
    )

    return request


def parse_response(response: httpx.Response) -> Follows:
    raise_for_status(response)

    res_json = jsonlib.loads(response.content)
    if code := int(res_json['error_code']):
        raise TiebaServerError(code, res_json['error_msg'])

    follows = Follows(res_json)

    return follows
