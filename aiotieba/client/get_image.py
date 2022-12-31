from typing import Literal

import cv2 as cv
import httpx
import numpy as np

from .._exception import ContentTypeError
from .common.helper import raise_for_status, url


def _pack_request_without_host(client: httpx.AsyncClient, url: str) -> httpx.Request:
    request = httpx.Request("GET", url, headers=client.headers, cookies=client.cookies)
    return request


def pack_request(client: httpx.AsyncClient, url: str) -> httpx.Request:
    request = _pack_request_without_host(client, url)
    request.headers["Host"] = request.url.host
    return request


def pack_request_hash(client: httpx.AsyncClient, raw_hash: str, size: Literal['s', 'm', 'l']) -> httpx.Request:

    if size == 's':
        img_url = url("http", "imgsrc.baidu.com", f"/forum/w=720;q=60;g=0/sign=__/{raw_hash}.jpg")
    elif size == 'm':
        img_url = url("http", "imgsrc.baidu.com", f"/forum/w=960;q=60;g=0/sign=__/{raw_hash}.jpg")
    elif size == 'l':
        img_url = url("http", "imgsrc.baidu.com", f"/forum/pic/item/{raw_hash}.jpg")
    else:
        raise ValueError(f"Invalid size={size}")

    request = _pack_request_without_host(client, img_url)
    request.headers["Host"] = "imgsrc.baidu.com"

    return request


def pack_request_portrait(client: httpx.AsyncClient, portrait: str, size: Literal['s', 'm', 'l']) -> httpx.Request:

    if size == 's':
        path = 'n'
    elif size == 'm':
        path = ''
    elif size == 'l':
        path = 'h'
    else:
        raise ValueError(f"Invalid size={size}")
    img_url = url("http", "tb.himg.baidu.com", f"/sys/portrait{path}/item/{portrait}")

    request = _pack_request_without_host(client, img_url)
    request.headers["Host"] = "tb.himg.baidu.com"

    return request


def parse_response(response: httpx.Response) -> np.ndarray:
    raise_for_status(response)

    content_type = response.headers["Content-Type"]
    if not content_type.endswith(('jpeg', 'png', 'bmp'), 6):
        raise ContentTypeError(f"Expect jpeg, png or bmp, got {content_type}")

    image = cv.imdecode(np.frombuffer(response.content, np.uint8), cv.IMREAD_COLOR)
    if image is None:
        raise RuntimeError("Error in cv2.imdecode")

    return image
