import bs4
import httpx

from .common.typedef import MemberUsers


def pack_request(client: httpx.AsyncClient, fname: str, pn: int) -> httpx.Request:
    request = httpx.Request(
        "GET",
        "https://tieba.baidu.com/bawu2/platform/listMemberInfo",
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
    response.raise_for_status()

    soup = bs4.BeautifulSoup(response.text, 'lxml')
    member_users = MemberUsers(soup)

    return member_users
