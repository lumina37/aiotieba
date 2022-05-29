# -*- coding:utf-8 -*-
__all__ = ['SCRIPT_PATH', 'MODULE_DIR', 'CONFIG']

import sys
from pathlib import Path
from typing import Dict

import yaml

SCRIPT_PATH = Path(sys.argv[0])
MODULE_DIR = Path(__file__).parent

with (SCRIPT_PATH.parent / 'config/config.yaml').open('r', encoding='utf-8') as file:
    CONFIG: Dict[str, Dict[str, str]] = yaml.load(file, Loader=yaml.SafeLoader)
if not (CONFIG.__contains__('BDUSS') and isinstance(CONFIG['BDUSS'], dict)):
    CONFIG['BDUSS'] = {}
if not (CONFIG.__contains__('STOKEN') and isinstance(CONFIG['STOKEN'], dict)):
    CONFIG['STOKEN'] = {}
if not (CONFIG.__contains__('database') and isinstance(CONFIG['database'], dict)):
    CONFIG['database'] = {}
if not (CONFIG.__contains__('fname_zh2en') and isinstance(CONFIG['fname_zh2en'], dict)):
    CONFIG['fname_zh2en'] = {}
