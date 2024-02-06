"""
Asynchronous I/O Client/Reviewer for Baidu Tieba

@Author: starry.qvq@gmail.com
@License: Unlicense
@Documentation: https://aiotieba.cc/
"""

import os

from . import const, core, enums, exception, logging, typing
from .__version__ import __version__
from .client import Client
from .config import TimeoutConfig
from .core import Account
from .enums import *  # noqa: F403
from .logging import enable_filelog, get_logger

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
