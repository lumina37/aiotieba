import sys

import aiohttp
import cv2 as cv
import numpy as np
import yarl

from .._core import TbCore
from .._exception import ContentTypeError, HTTPStatusError
from .._helper import log_exception, pack_web_get_request, send_request


def headers_checker(response: aiohttp.ClientResponse) -> None:
    if response.status != 200:
        raise HTTPStatusError(response.status, response.reason)

    if not response.content_type.endswith(('jpeg', 'png', 'bmp'), 6):
        raise ContentTypeError(f"Expect jpeg, png or bmp, got {response.content_type}")


def parse_body(body: bytes) -> "np.ndarray":
    image = cv.imdecode(np.frombuffer(body, np.uint8), cv.IMREAD_COLOR)
    if image is None:
        raise RuntimeError("Error in cv2.imdecode")

    return image


async def request(connector: aiohttp.TCPConnector, core: TbCore, url: yarl.URL) -> "np.ndarray":
    request = pack_web_get_request(core, url, [])

    try:
        body = await send_request(request, connector, read_bufsize=512 * 1024, headers_checker=headers_checker)
        image = parse_body(body)

    except Exception as err:
        log_exception(sys._getframe(1), err, f"url={url}")
        image = np.empty(0, dtype=np.uint8)

    return image
