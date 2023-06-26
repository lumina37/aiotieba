import bs4
import yarl

from ...const import WEB_BASE_HOST
from ...core import HttpCore
from ._classdef import BlacklistUsers


def parse_body(body: bytes) -> BlacklistUsers:
    soup = bs4.BeautifulSoup(body, 'lxml')
    blacklist_users = BlacklistUsers(soup)

    return blacklist_users


async def request(http_core: HttpCore, fname: str, pn: int) -> BlacklistUsers:
    params = [
        ('word', fname),
        ('pn', pn),
    ]

    request = http_core.pack_web_get_request(
        yarl.URL.build(scheme="https", host=WEB_BASE_HOST, path="/bawu2/platform/listBlackUser"), params
    )

    __log__ = "fname={fname}"  # noqa: F841

    body = await http_core.net_core.send_request(request, read_bufsize=64 * 1024)
    return parse_body(body)
