# -*- coding:utf-8 -*-
"""
@Version 2.3.2_rc3
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
from .reviewer import Reviewer


def terminate(signalNumber, frame):
    raise KeyboardInterrupt


signal.signal(signal.SIGTERM, terminate)
