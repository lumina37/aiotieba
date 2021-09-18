# -*- coding:utf-8 -*-
"""
@Author: Starry
@License: MIT
@Homepage: https://github.com/Starry-OvO/Tieba-Cloud-Review
@Required Modules:
    pip install pymysql
    pip install lxml
    pip install bs4
    pip install pillow
    pip install imagehash

    可能需要的第三方yum源: Raven(https://centos.pkgs.org/8/raven-x86_64/raven-release-1.0-1.el8.noarch.rpm.html)
    使用 [rpm -Uvh xxx.rpm] 来安装Raven源
    用 [sudo yum install zbar-devel] 来安装zbar支持
    用 [pip install pyzbar] 来安装pyzbar
"""

import signal

from .cloud_review import CloudReview
from .data_structure import *
from .logger import log
from .utils import Browser


def terminate(signalNumber, frame):
    import sys
    sys.exit()


signal.signal(signal.SIGTERM, terminate)
