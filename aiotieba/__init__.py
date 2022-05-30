# -*- coding:utf-8 -*-
"""
@Version: 2.7.2
@Author: starry.qvq@gmail.com
@License: Unlicense
@Homepage: https://github.com/Starry-OvO/Tieba-Manager
@Required Python Version: 3.8+
@Required Modules: pyyaml aiohttp protobuf lxml beautifulsoup4 pycryptodome aiomysql opencv-contrib-python
"""

import signal

from .client import *
from .logger import *
from .reviewer import *
from .types import *

log = get_logger()


def terminate(signal_number, frame):
    raise KeyboardInterrupt


signal.signal(signal.SIGTERM, terminate)
