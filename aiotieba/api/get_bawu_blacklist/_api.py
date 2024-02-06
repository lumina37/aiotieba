import bs4
import yarl

from ...const import WEB_BASE_HOST
from ...core import HttpCore
from ._classdef import BawuBlacklistUsers


def parse_body(body: bytes) -> BawuBlacklistUsers:
    soup = bs4.BeautifulSoup(body, 'lxml')
    bawu_blacklist_users = BawuBlacklistUsers.from_tbdata(soup)

    return bawu_blacklist_users


async def request(http_core: HttpCore, fname: str, pn: int) -> BawuBlacklistUsers:
    params = [
        ('word', fname),
        ('pn', pn),
    ]

    request = http_core.pack_web_get_request(
        yarl.URL.build(scheme="https", host=WEB_BASE_HOST, path="/bawu2/platform/listBlackUser"), params
    )

    body = await http_core.net_core.send_request(request, read_bufsize=64 * 1024)
    return parse_body(body)
