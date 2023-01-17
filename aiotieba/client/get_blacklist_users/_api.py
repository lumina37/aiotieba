import bs4
import httpx

from .._helper import WEB_BASE_HOST, raise_for_status, url
from ._classdef import BlacklistUsers


def pack_request(client: httpx.AsyncClient, fname: str, pn: int) -> httpx.Request:
    request = httpx.Request(
        "GET",
        url("https", WEB_BASE_HOST, "/bawu2/platform/listBlackUser"),
        params={
            'word': fname,
            'pn': pn,
        },
        headers=client.headers,
        cookies=client.cookies,
    )

    return request


def parse_response(response: httpx.Response) -> BlacklistUsers:
    raise_for_status(response)

    soup = bs4.BeautifulSoup(response.text, 'lxml')
    blacklist_users = BlacklistUsers()._init(soup)

    return blacklist_users
