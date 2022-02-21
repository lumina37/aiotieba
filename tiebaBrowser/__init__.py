# -*- coding:utf-8 -*-
"""
@Author: Starry
@License: MIT
@Homepage: https://github.com/Starry-OvO/Tieba-Cloud-Review
@Require Python 3.9+
@Basic Required Modules: requests,lxml,bs4
@CloudReview Required Modules: pymysql,pillow,pyzbar
"""

import signal

from .api import Browser
from .data_structure import *
from .logger import log


def terminate(signalNumber, frame):
    import sys
    sys.exit()


signal.signal(signal.SIGTERM, terminate)
