# -*- coding:utf-8 -*-
__all__ = [
    'SCRIPT_PATH',
    'SCRIPT_DIR',
    'MODULE_DIR',
]

from pathlib import Path
import sys


SCRIPT_PATH = Path(sys.argv[0])
SCRIPT_DIR = SCRIPT_PATH.parent
MODULE_DIR = Path(__file__).parent
