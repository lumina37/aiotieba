import bs4
import yarl

from ...const import WEB_BASE_HOST
from ...core import HttpCore
from ...request import pack_web_get_request, send_request
from ._classdef import RankUsers


def parse_body(body: bytes) -> RankUsers:
    soup = bs4.BeautifulSoup(body, 'lxml')
    rank_users = RankUsers(soup)

    return rank_users


async def request(http_core: HttpCore, fname: str, pn: int) -> RankUsers:
    params = [
        ('kw', fname),
        ('pn', pn),
        ('ie', 'utf-8'),
    ]

    request = pack_web_get_request(
        http_core,
        yarl.URL.build(scheme="https", host=WEB_BASE_HOST, path="/f/like/furank"),
        params,
    )

    __log__ = "fname={fname}"  # noqa: F841

    body = await send_request(request, http_core.network, read_bufsize=64 * 1024)
    return parse_body(body)
