import bs4
import httpx

from .common.typedef import BlacklistUsers


def pack_request(client: httpx.AsyncClient, fname: str, pn: int) -> httpx.Request:
    request = httpx.Request(
        "GET",
        "https://tieba.baidu.com/bawu2/platform/listBlackUser",
        params={
            'word': fname,
            'pn': pn,
        },
        headers=client.headers,
        cookies=client.cookies,
    )

    return request


def parse_response(response: httpx.Response) -> BlacklistUsers:
    response.raise_for_status()

    soup = bs4.BeautifulSoup(response.text, 'lxml')
    blacklist_users = BlacklistUsers(soup)

    return blacklist_users
