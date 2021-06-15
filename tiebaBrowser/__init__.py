# -*- coding:utf-8 -*-
"""
@Author: Starry
@License: MIT
@Homepage: https://github.com/Starry-OvO
@Required Modules:
    sudo pip install mysql-connector
    sudo pip install lxml
    sudo pip install bs4
    sudo pip install pillow
    sudo pip install imagehash
    sudo pip install pypinyin

    可能需要的第三方yum源: Raven(https://centos.pkgs.org/8/raven-x86_64/raven-release-1.0-1.el8.noarch.rpm.html)
    使用 [rpm -Uvh xxx.rpm] 来安装Raven源
    用 [sudo yum install zbar-devel] 来安装zbar支持
    用 [sudo pip install pyzbar] 来安装pyzbar
"""

from .data_structure import *
from .logger import log
from .utils import *
from .cloud_review import *

import signal
def terminate(signalNumber, frame):
    import sys
    sys.exit()
signal.signal(signal.SIGTERM, terminate)
