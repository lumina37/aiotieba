import datetime
from typing import Optional

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
    start_dt: Optional[datetime.datetime],
    end_dt: Optional[datetime.datetime],
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
        extend_params = [
            ('svalue', search_value),
            ('stype', 'post_uname' if search_type == BawuSearchType.USER else 'op_uname'),
            ('begin', int(start_dt.timestamp())),
            ('end', int(end_dt.timestamp())),
        ]
        params += extend_params

    request = http_core.pack_web_get_request(
        yarl.URL.build(scheme="https", host=WEB_BASE_HOST, path="/bawu2/platform/listPostLog"), params
    )

    body = await http_core.net_core.send_request(request, read_bufsize=64 * 1024)
    return parse_body(body)
