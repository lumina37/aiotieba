# -*- coding:utf-8 -*-
"""
@Version: 2.8.1_beta
@Author: starry.qvq@gmail.com
@License: Unlicense
@Homepage: https://github.com/Starry-OvO/Tieba-Manager
@Required Python Version: 3.9+
@Required Modules: tomli aiohttp protobuf lxml beautifulsoup4 pycryptodome aiomysql numpy opencv-contrib-python
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

elif os.name == 'nt':
    import asyncio

    # To fix "RuntimeError: Event loop is closed" occured in _ProactorBasePipeTransport.__del__
    # See: https://github.com/aio-libs/aiohttp/issues/4324
    # The future version of asyncio will fix this bug. See: https://github.com/python/cpython/pull/92842
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
