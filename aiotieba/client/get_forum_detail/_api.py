import sys

import aiohttp
import yarl

from .._core import APP_BASE_HOST, TbCore
from .._exception import TiebaServerError
from .._helper import APP_INSECURE_SCHEME, log_exception, pack_form_request, parse_json, send_request
from ._classdef import Forum_detail


def parse_body(body: bytes) -> Forum_detail:
    res_json = parse_json(body)
    if code := int(res_json['error_code']):
        raise TiebaServerError(code, res_json['error_msg'])

    forum_dict = res_json['forum_info']
    forum = Forum_detail()._init(forum_dict)

    return forum


async def request(connector: aiohttp.TCPConnector, core: TbCore, fid: int) -> Forum_detail:

    data = [
        ('_client_version', core.main_version),
        ('forum_id', fid),
    ]

    request = pack_form_request(
        core,
        yarl.URL.build(scheme=APP_INSECURE_SCHEME, host=APP_BASE_HOST, path="/c/f/forum/getforumdetail"),
        data,
    )

    try:
        body = await send_request(request, connector, read_bufsize=8 * 1024)
        forum = parse_body(body)

    except Exception as err:
        log_exception(sys._getframe(1), err, f"fid={fid}")
        forum = Forum_detail()._init_null()

    return forum
