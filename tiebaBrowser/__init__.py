# -*- coding:utf-8 -*-
"""
@Version 2.3.5_rc_1
@Author: Starry
@License: Unlicense
@Homepage: https://github.com/Starry-OvO/Tieba-Cloud-Review
@Require Python 3.9+
@Required Modules: asyncio aiohttp lxml bs4 pymysql pillow opencv-contrib-python protobuf
"""

import asyncio
import signal
import sys

from ._api import Browser
from ._logger import log
from ._types import *
from .reviewer import Reviewer


def terminate(signal_number, frame):
    raise KeyboardInterrupt


signal.signal(signal.SIGTERM, terminate)

if sys.platform == "win32" and sys.version_info.minor >= 8:
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
