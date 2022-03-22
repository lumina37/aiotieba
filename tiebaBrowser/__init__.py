# -*- coding:utf-8 -*-
"""
@Version 2.0.1_rc1
@Author: Starry
@License: Unlicense
@Homepage: https://github.com/Starry-OvO/Tieba-Cloud-Review
@Require Python 3.9+
@Required Modules: asyncio aiohttp lxml bs4 pymysql pillow opencv-contrib-python protobuf
"""

import signal

from .api import Browser
from .cloud_review import CloudReview
from .data_structure import *
from .logger import log


def terminate(signalNumber, frame):
    raise KeyboardInterrupt


signal.signal(signal.SIGTERM, terminate)
