# -*- coding:utf-8 -*-
"""
@Author: starry.qvq@gmail.com
@License: Unlicense
@Homepage: https://github.com/Starry-OvO/Tieba-Manager
"""

import os

from .client import *
from .log import *
from .reviewer import *
from .typedefs import *

__version__ = "2.8.1"

if os.name == 'posix':
    import signal

    def terminate(signal_number, frame):
        raise KeyboardInterrupt

    signal.signal(signal.SIGTERM, terminate)

elif os.name == 'nt':
    import asyncio

    # 此举是为了规避 _ProactorBasePipeTransport.__del__ 中的 RuntimeError: Event loop is closed
    # 参考: https://github.com/aio-libs/aiohttp/issues/4324
    # 将来的asyncio版本会修复该bug
    # 参考: https://github.com/python/cpython/pull/92842
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
