"""
@Author: starry.qvq@gmail.com
@License: Unlicense
@Homepage: https://github.com/Starry-OvO/Tieba-Manager
"""

import os

from ._logger import *
from .client import *
from .reviewer import *
from .typedefs import *

__version__ = "2.9.0.beta1"

if os.name == 'posix':
    import signal

    def terminate(signal_number, frame):
        raise KeyboardInterrupt

    signal.signal(signal.SIGTERM, terminate)
