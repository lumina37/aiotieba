# -*- coding:utf-8 -*-
__all__ = ['SCRIPT_PATH', 'MODULE_DIR', 'CONFIG']

import json
import sys
from pathlib import Path

SCRIPT_PATH = Path(sys.argv[0])
MODULE_DIR = Path(__file__).parent

with (SCRIPT_PATH.parent / 'config/config.json').open('r', encoding='utf-8') as file:
    CONFIG: dict = json.load(file)
if not CONFIG.__contains__('BDUSS'):
    CONFIG['BDUSS'] = {}
if not isinstance(CONFIG['BDUSS'], dict):
    CONFIG['BDUSS'] = {}
if not CONFIG.__contains__('MySQL'):
    CONFIG['MySQL'] = {}
if not isinstance(CONFIG['MySQL'], dict):
    CONFIG['MySQL'] = {}
if not CONFIG.__contains__('fname_mapping'):
    CONFIG['fname_mapping'] = {}
if not isinstance(CONFIG['fname_mapping'], dict):
    CONFIG['fname_mapping'] = {}
