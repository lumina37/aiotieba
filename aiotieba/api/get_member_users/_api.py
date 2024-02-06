import bs4
import yarl

from ...const import WEB_BASE_HOST
from ...core import HttpCore
from ._classdef import MemberUsers


def parse_body(body: bytes) -> MemberUsers:
    soup = bs4.BeautifulSoup(body, 'lxml')
    member_users = MemberUsers.from_tbdata(soup)

    return member_users


async def request(http_core: HttpCore, fname: str, pn: int) -> MemberUsers:
    params = [
        ('word', fname),
        ('pn', pn),
        ('ie', 'utf-8'),
    ]

    request = http_core.pack_web_get_request(
        yarl.URL.build(scheme="https", host=WEB_BASE_HOST, path="/bawu2/platform/listMemberInfo"), params
    )

    body = await http_core.net_core.send_request(request, read_bufsize=64 * 1024)
    return parse_body(body)
