import bs4
import httpx

from .common.typedef import RankUsers


def pack_request(client: httpx.AsyncClient, fname: str, pn: int) -> httpx.Request:
    request = httpx.Request(
        "GET",
        "https://tieba.baidu.com/f/like/furank",
        params={
            'kw': fname,
            'pn': pn,
            'ie': 'utf-8',
        },
        headers=client.headers,
        cookies=client.cookies,
    )

    return request


def parse_response(response: httpx.Response) -> RankUsers:
    response.raise_for_status()

    soup = bs4.BeautifulSoup(response.text, 'lxml')
    rank_users = RankUsers(soup)

    return rank_users
