import bs4
import yarl

from ...const import WEB_BASE_HOST
from ...core import HttpCore
from ...enums import RankForumType
from ._classdef import RankForums


def parse_body(body: bytes) -> RankForums:
    soup = bs4.BeautifulSoup(body, 'lxml')
    bawu_postlogs = RankForums.from_tbdata(soup)

    return bawu_postlogs


async def request(http_core: HttpCore, fname: str, pn: int, rank_type: RankForumType) -> RankForums:
    params = [
        ('kw', fname),
        ('type', int(rank_type)),
        ('pn', pn),
        ('ie', 'utf-8'),
    ]

    request = http_core.pack_web_get_request(
        yarl.URL.build(scheme="https", host=WEB_BASE_HOST, path="/sign/index"), params
    )

    body = await http_core.net_core.send_request(request, read_bufsize=8 * 1024)
    return parse_body(body)
