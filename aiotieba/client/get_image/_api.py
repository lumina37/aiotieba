from typing import TYPE_CHECKING

import aiohttp
import yarl

from .._core import TbCore
from .._helper import pack_web_get_request
from ._request import img_send_request

if TYPE_CHECKING:
    import numpy as np


async def request(connector: aiohttp.TCPConnector, core: TbCore, url: yarl.URL) -> bytes:
    request = pack_web_get_request(core, url, [])
    body = await img_send_request(request, connector)
    return body


def parse_body(body: bytes) -> "np.ndarray":
    import cv2 as cv
    import numpy as np

    image = cv.imdecode(np.frombuffer(body, np.uint8), cv.IMREAD_COLOR)
    if image is None:
        raise RuntimeError("Error in cv2.imdecode")

    return image
