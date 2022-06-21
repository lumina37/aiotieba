# -*- coding:utf-8 -*-
__all__ = ['SCRIPT_PATH', 'SCRIPT_DIR', 'MODULE_DIR', 'CONFIG']

import sys
from pathlib import Path
from typing import Dict

SCRIPT_PATH = Path(sys.argv[0])
SCRIPT_DIR = SCRIPT_PATH.parent
MODULE_DIR = Path(__file__).parent


try:
    with (SCRIPT_DIR / "config/config.yaml").open('r', encoding='utf-8') as file:

        import yaml

        CONFIG: Dict[str, Dict[str, str]] = yaml.load(file, Loader=yaml.SafeLoader)

except FileNotFoundError:

    import shutil

    config_dir = SCRIPT_DIR / "config"
    config_dir.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(str(MODULE_DIR / "config_example/minimal.yaml"), str(config_dir / "config.yaml"))
    shutil.copyfile(str(MODULE_DIR / "config_example/full.yaml"), str(config_dir / "config_full_example.yaml"))

    CONFIG = {}

required_keys = ['BDUSS', 'STOKEN', 'database']
for required_key in required_keys:
    if not (CONFIG.__contains__(required_key) and isinstance(CONFIG[required_key], dict)):
        CONFIG[required_key] = {}
