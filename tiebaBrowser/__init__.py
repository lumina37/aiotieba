# -*- coding:utf-8 -*-
"""
@Author: Starry
@License: MIT
@Homepage: https://github.com/Starry-OvO/Tieba-Cloud-Review
@Require Python 3.7+
@Required Modules:
    pip install pymysql
    pip install lxml
    pip install bs4
    pip install pillow
    pip install imagehash
    yum install zbar-devel
    pip install pyzbar
"""

import signal

from .api import Browser
from .data_structure import *
from .logger import log


def terminate(signalNumber, frame):
    import sys
    sys.exit()


signal.signal(signal.SIGTERM, terminate)
