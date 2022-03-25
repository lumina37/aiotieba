# -*- coding:utf-8 -*-
"""
@Version 2.1.0
@Author: Starry
@License: Unlicense
@Homepage: https://github.com/Starry-OvO/Tieba-Cloud-Review
@Require Python 3.9+
@Required Modules: asyncio aiohttp lxml bs4 pymysql pillow opencv-contrib-python protobuf
"""

import signal

from ._api import Browser
from ._logger import log
from ._types import *
from .cloud_review import CloudReview


def terminate(signalNumber, frame):
    raise KeyboardInterrupt


signal.signal(signal.SIGTERM, terminate)
