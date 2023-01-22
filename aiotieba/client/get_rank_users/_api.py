import sys

import aiohttp
import bs4
import yarl

from .._core import WEB_BASE_HOST, TbCore
from .._helper import log_exception, pack_web_get_request, send_request
from ._classdef import RankUsers


def parse_body(body: bytes) -> RankUsers:
    soup = bs4.BeautifulSoup(body, 'lxml')
    rank_users = RankUsers()._init(soup)

    return rank_users


async def request(connector: aiohttp.TCPConnector, core: TbCore, fname: str, pn: int) -> RankUsers:

    params = [
        ('kw', fname),
        ('pn', pn),
        ('ie', 'utf-8'),
    ]

    request = pack_web_get_request(
        core,
        yarl.URL.build(scheme="https", host=WEB_BASE_HOST, path="/f/like/furank"),
        params,
    )

    try:
        body = await send_request(request, connector, read_bufsize=64 * 1024)
        rank_users = parse_body(body)

    except Exception as err:
        log_exception(sys._getframe(1), err, f"fname={fname}")
        rank_users = RankUsers()._init_null()

    return rank_users
