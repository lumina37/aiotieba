from __future__ import annotations

import datetime
import time
from urllib.parse import quote

import bs4
import yarl

from ...const import WEB_BASE_HOST
from ...core import HttpCore
from ...enums import BawuSearchType
from ._classdef import Postlogs


def parse_body(body: bytes) -> Postlogs:
    soup = bs4.BeautifulSoup(body, 'lxml')
    bawu_postlogs = Postlogs.from_tbdata(soup)

    return bawu_postlogs


async def request(
    http_core: HttpCore,
    fname: str,
    pn: int,
    search_value: str,
    search_type: BawuSearchType,
    start_dt: datetime.datetime | None,
    end_dt: datetime.datetime | None,
    op_type: int,
) -> Postlogs:
    params = [
        ('word', fname),
        ('pn', pn),
        ('ie', 'utf-8'),
    ]

    if op_type:
        params.append(('op_type', op_type))

    if search_value:
        if search_type == BawuSearchType.USER:
            search_value = quote(search_value)
            extend_params = [
                ('svalue', search_value),
                ('stype', 'post_uname'),
            ]
        else:
            extend_params = [
                ('svalue', search_value),
                ('stype', 'op_uname'),
            ]
        params += extend_params

    if start_dt:
        begin = int(start_dt.timestamp())
        if end_dt is None:
            end = int(time.time())
        else:
            end = int(end_dt.timestamp())
        extend_params = [
            ('end', end),
            ('begin', begin),
        ]
        params += extend_params

    request = http_core.pack_web_get_request(
        yarl.URL.build(scheme="https", host=WEB_BASE_HOST, path="/bawu2/platform/listPostLog"), params
    )

    body = await http_core.net_core.send_request(request, read_bufsize=32 * 1024)
    return parse_body(body)
