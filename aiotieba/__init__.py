# -*- coding:utf-8 -*-
"""
@Version 2.7.1_beta
@Author: starry.qvq@gmail.com
@License: Unlicense
@Homepage: https://github.com/Starry-OvO/Tieba-Manager
@Required Python Version: 3.8+
@Required Modules: pyyaml aiohttp[speedups] protobuf lxml beautifulsoup4 pycryptodome aiomysql opencv-contrib-python
"""

import asyncio
import signal
import sys

from .api import *
from .logger import *
from .reviewer import *
from .types import *

log = get_logger()


def terminate(signal_number, frame):
    raise KeyboardInterrupt


signal.signal(signal.SIGTERM, terminate)

if sys.platform == "win32" and sys.version_info.minor >= 8:
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
