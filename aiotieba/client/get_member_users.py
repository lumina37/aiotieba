import bs4
import httpx

from .common.helper import raise_for_status, url
from .common.typedef import MemberUsers


def pack_request(client: httpx.AsyncClient, fname: str, pn: int) -> httpx.Request:
    request = httpx.Request(
        "GET",
        url("https", "tieba.baidu.com", "/bawu2/platform/listMemberInfo"),
        params={
            'word': fname,
            'pn': pn,
            'ie': 'utf-8',
        },
        headers=client.headers,
        cookies=client.cookies,
    )

    return request


def parse_response(response: httpx.Response) -> MemberUsers:
    raise_for_status(response)

    soup = bs4.BeautifulSoup(response.text, 'lxml')
    member_users = MemberUsers(soup)

    return member_users
