import aiohttp
import bs4
import yarl

from .._core import WEB_BASE_HOST, TbCore
from .._helper import pack_web_get_request, send_request
from ._classdef import MemberUsers


async def request(connector: aiohttp.TCPConnector, core: TbCore, fname: str, pn: int) -> bytes:

    params = [
        ('word', fname),
        ('pn', pn),
        ('ie', 'utf-8'),
    ]

    request = pack_web_get_request(
        core,
        yarl.URL.build(scheme="https", host=WEB_BASE_HOST, path="/bawu2/platform/listMemberInfo"),
        params,
    )

    body = await send_request(request, connector, read_bufsize=64 * 1024)

    return body


def parse_body(body: bytes) -> MemberUsers:
    soup = bs4.BeautifulSoup(body, 'lxml')
    member_users = MemberUsers()._init(soup)

    return member_users
