import aiohttp
import yarl

from .._core import APP_BASE_HOST, TbCore
from .._exception import TiebaServerError
from .._helper import APP_NON_SECURE_SCHEME, pack_form_request, parse_json, send_request
from ._classdef import Forum_detail


async def request(connector: aiohttp.TCPConnector, core: TbCore, fid: int) -> bytes:

    data = [
        ('_client_version', core.main_version),
        ('forum_id', fid),
    ]

    request = pack_form_request(
        core,
        yarl.URL.build(scheme=APP_NON_SECURE_SCHEME, host=APP_BASE_HOST, path="/c/f/forum/getforumdetail"),
        data,
    )

    body = await send_request(request, connector, read_bufsize=8 * 1024)

    return body


def parse_body(body: bytes) -> Forum_detail:
    res_json = parse_json(body)
    if code := int(res_json['error_code']):
        raise TiebaServerError(code, res_json['error_msg'])

    forum_dict = res_json['forum_info']
    forum = Forum_detail()._init(forum_dict)

    return forum
