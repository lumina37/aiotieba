"""
Asynchronous I/O Client/Reviewer for Baidu Tieba

@Author: starry.qvq@gmail.com
@License: Unlicense
@Documentation: https://aiotieba.cc/
"""

import os

from .__version__ import __version__
from ._logging import get_logger as LOG
from .client import Client, const, core, crypto, enums, exception, typing

if os.name == 'posix':
    import signal

    def terminate(signal_number, frame):
        raise KeyboardInterrupt

    signal.signal(signal.SIGTERM, terminate)

    try:
        import asyncio

        import uvloop

        if not isinstance(asyncio.get_event_loop_policy(), uvloop.EventLoopPolicy):
            asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

    except ImportError:
        pass
