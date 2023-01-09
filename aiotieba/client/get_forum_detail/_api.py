import httpx

from .._classdef.core import TiebaCore
from .._exception import TiebaServerError
from .._helper import APP_BASE_HOST, pack_form_request, parse_json, raise_for_status, sign, url
from ._classdef import Forum_detail


def pack_request(client: httpx.AsyncClient, core: TiebaCore, fid: int) -> httpx.Request:

    data = [
        ('_client_version', core.main_version),
        ('forum_id', fid),
    ]

    request = pack_form_request(
        client,
        url("http", APP_BASE_HOST, "/c/f/forum/getforumdetail"),
        sign(data),
    )

    return request


def parse_response(response: httpx.Response) -> Forum_detail:
    raise_for_status(response)

    res_json = parse_json(response.content)
    if code := int(res_json['error_code']):
        raise TiebaServerError(code, res_json['error_msg'])

    forum_dict = res_json['forum_info']
    forum = Forum_detail()._init(forum_dict)

    return forum
