from typing import TYPE_CHECKING

import aiohttp
import yarl

from ...core import HttpCore
from ...exception import ContentTypeError, HTTPStatusError

if TYPE_CHECKING:
    import numpy as np


def null_ret_factory() -> "np.ndarray":
    import numpy as np

    return np.empty(0, dtype=np.uint8)


def headers_checker(response: aiohttp.ClientResponse) -> None:
    if response.status != 200:
        raise HTTPStatusError(response.status, response.reason)

    if not response.content_type.endswith(('jpeg', 'png', 'bmp'), 6):
        raise ContentTypeError(f"Expect jpeg, png or bmp, got {response.content_type}")


def parse_body(body: bytes) -> "np.ndarray":
    import cv2 as cv
    import numpy as np

    image = cv.imdecode(np.frombuffer(body, np.uint8), cv.IMREAD_COLOR)
    if image is None:
        raise RuntimeError("Error in cv2.imdecode")

    return image


async def request(http_core: HttpCore, url: yarl.URL) -> "np.ndarray":
    request = http_core.pack_web_get_request(url, [])

    __log__ = "url={url}"  # noqa: F841

    body = await http_core.net_core.send_request(request, read_bufsize=512 * 1024, headers_checker=headers_checker)
    return parse_body(body)
