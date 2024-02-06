import aiohttp
import yarl

from ...core import HttpCore
from ...exception import ContentTypeError, HTTPStatusError
from ._classdef import Image, ImageBytes


def _headers_checker(response: aiohttp.ClientResponse) -> None:
    if response.status != 200:
        raise HTTPStatusError(response.status, response.reason)

    if not response.content_type.endswith(('jpeg', 'png', 'bmp'), 6):
        raise ContentTypeError(f"Expect jpeg, png or bmp, got {response.content_type}")


def parse_body(body: bytes) -> Image:
    import cv2 as cv
    import numpy as np

    image = cv.imdecode(np.frombuffer(body, np.uint8), cv.IMREAD_COLOR)
    if image is None:
        raise RuntimeError("Error in cv2.imdecode")

    return Image(image)


async def request_bytes(http_core: HttpCore, url: yarl.URL) -> ImageBytes:
    request = http_core.pack_web_get_request(url, [])

    body = await http_core.net_core.send_request(request, read_bufsize=256 * 1024, headers_checker=_headers_checker)

    return ImageBytes(body)


async def request(http_core: HttpCore, url: yarl.URL) -> Image:
    body = await request_bytes(http_core, url)
    return parse_body(body)
