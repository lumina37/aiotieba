# -*- coding:utf-8 -*-
"""
@Version: 2.7.5
@Author: starry.qvq@gmail.com
@License: Unlicense
@Homepage: https://github.com/Starry-OvO/Tieba-Manager
@Required Python Version: 3.9+
@Required Modules: tomli aiohttp protobuf lxml beautifulsoup4 pycryptodome aiomysql opencv-contrib-python
"""

import os

from .client import *
from .logger import *
from .reviewer import *
from .types import *

if os.name == 'posix':
    import signal

    def terminate(signal_number, frame):
        raise KeyboardInterrupt

    signal.signal(signal.SIGTERM, terminate)
