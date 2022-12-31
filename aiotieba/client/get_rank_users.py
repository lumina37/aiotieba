import bs4
import httpx

from .common.helper import raise_for_status, url
from .common.typedef import RankUsers


def pack_request(client: httpx.AsyncClient, fname: str, pn: int) -> httpx.Request:
    request = httpx.Request(
        "GET",
        url("https", "tieba.baidu.com", "/f/like/furank"),
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
    raise_for_status(response)

    soup = bs4.BeautifulSoup(response.text, 'lxml')
    rank_users = RankUsers(soup)

    return rank_users
