import sys

import aiohttp
import bs4
import yarl

from .._core import WEB_BASE_HOST, TbCore
from .._helper import log_exception, pack_web_get_request, send_request
from ._classdef import BlacklistUsers


def parse_body(body: bytes) -> BlacklistUsers:
    soup = bs4.BeautifulSoup(body, 'lxml')
    blacklist_users = BlacklistUsers()._init(soup)

    return blacklist_users


async def request(connector: aiohttp.TCPConnector, core: TbCore, fname: str, pn: int) -> BlacklistUsers:

    params = [
        ('word', fname),
        ('pn', pn),
    ]

    request = pack_web_get_request(
        core,
        yarl.URL.build(scheme="https", host=WEB_BASE_HOST, path="/bawu2/platform/listBlackUser"),
        params,
    )

    try:
        body = await send_request(request, connector, read_bufsize=64 * 1024)
        blacklist_users = parse_body(body)

    except Exception as err:
        log_exception(sys._getframe(1), err, f"fname={fname}")
        blacklist_users = BlacklistUsers()._init_null()

    return blacklist_users
