import bs4
import yarl

from ...const import WEB_BASE_HOST
from ...core import HttpCore
from ._classdef import RankUsers


def parse_body(body: bytes) -> RankUsers:
    soup = bs4.BeautifulSoup(body, 'lxml')
    rank_users = RankUsers.from_tbdata(soup)

    return rank_users


async def request(http_core: HttpCore, fname: str, pn: int) -> RankUsers:
    params = [
        ('kw', fname),
        ('pn', pn),
        ('ie', 'utf-8'),
    ]

    request = http_core.pack_web_get_request(
        yarl.URL.build(scheme="https", host=WEB_BASE_HOST, path="/f/like/furank"), params
    )

    body = await http_core.net_core.send_request(request, read_bufsize=64 * 1024)
    return parse_body(body)
