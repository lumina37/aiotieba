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

required_keys = ['BDUSS', 'STOKEN', 'database', 'fname_zh2en']
for required_key in required_keys:
    if not (CONFIG.__contains__(required_key) and isinstance(CONFIG[required_key], dict)):
        CONFIG[required_key] = {}
