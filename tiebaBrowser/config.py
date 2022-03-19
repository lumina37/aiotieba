# -*- coding:utf-8 -*-
__all__ = ('SCRIPT_DIR', 'MODULE_DIR',
           'config')

import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(sys.argv[0])
MODULE_DIR = Path(__file__).parent

config = None
with (SCRIPT_DIR.parent / 'config/config.json').open('r', encoding='utf-8') as file:
    config = json.load(file)
if not config.__contains__('BDUSS'):
    config['BDUSS'] = {}
if type(config['BDUSS']) != dict:
    config['BDUSS'] = {}
if not config.__contains__('MySQL'):
    config['MySQL'] = {}
if type(config['MySQL']) != dict:
    config['MySQL'] = {}
if not config.__contains__('tieba_name_mapping'):
    config['tieba_name_mapping'] = {}
if type(config['tieba_name_mapping']) != dict:
    config['tieba_name_mapping'] = {}
