"""
Asynchronous I/O Client/Reviewer for Baidu Tieba

@Author: starry.qvq@gmail.com
@License: Unlicense
@Documentation: https://aiotieba.cc/
"""

import os

from .__version__ import __version__
from ._logging import get_logger as LOG
from .client import Client
from .client._classdef.enums import ReqUInfo
from .client._classdef.user import UserInfo
from .client._exception import ContentTypeError, HTTPStatusError, TiebaServerError
from .client._typing import (
    Appeal,
    Comment,
    Comments,
    Post,
    Posts,
    ShareThread,
    Thread,
    Threads,
    TypeFragAt,
    TypeFragEmoji,
    TypeFragImage,
    TypeFragItem,
    TypeFragLink,
    TypeFragmentUnknown,
    TypeFragText,
    TypeFragTiebaPlus,
    UserInfo_home,
)

if os.name == 'posix':
    import signal

    def terminate(signal_number, frame):
        raise KeyboardInterrupt

    signal.signal(signal.SIGTERM, terminate)
