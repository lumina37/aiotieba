# -*- coding:utf-8 -*-
__all__ = ('SCRIPT_DIR', 'MODULE_DIR',
           'config')

import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(sys.argv[0])
MODULE_DIR = Path(__file__).parent

config = None
try:
    with (SCRIPT_DIR.parent / 'config/config.json').open('r', encoding='utf-8') as file:
        config = json.load(file)
    if not config.__contains__('BDUSS'):
        raise AttributeError("config.json should contains key 'BDUSS'")
    if type(config['BDUSS']) is not dict:
        raise ValueError ("config['BDUSS'] should be dict")
    if not config.__contains__('MySQL'):
        raise AttributeError("config.json should contains key 'MySQL'")
    if type(config['MySQL']) is not dict:
        raise ValueError ("config['MySQL'] should be dict")
    if not config.__contains__('tieba_name_mapping'):
        raise AttributeError("config.json should contains key 'tieba_name_mapping'")
    if type(config['tieba_name_mapping']) is not dict:
        raise ValueError ("config['tieba_name_mapping'] should be dict")
except Exception:
    raise
