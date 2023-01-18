import aiohttp
import bs4
import yarl

from .._core import WEB_BASE_HOST, TbCore
from .._helper import pack_web_get_request, send_request
from ._classdef import BlacklistUsers


async def request(connector: aiohttp.TCPConnector, core: TbCore, fname: str, pn: int) -> bytes:

    params = [
        ('word', fname),
        ('pn', pn),
    ]

    request = pack_web_get_request(
        core,
        yarl.URL.build(scheme="https", host=WEB_BASE_HOST, path="/bawu2/platform/listBlackUser"),
        params,
    )

    body = await send_request(request, connector, read_bufsize=64 * 1024)

    return body


def parse_body(body: bytes) -> BlacklistUsers:
    soup = bs4.BeautifulSoup(body, 'lxml')
    blacklist_users = BlacklistUsers()._init(soup)

    return blacklist_users
