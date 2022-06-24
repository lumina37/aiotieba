# -*- coding:utf-8 -*-
__all__ = ['SCRIPT_PATH', 'SCRIPT_DIR', 'MODULE_DIR', 'CONFIG']

import sys
from pathlib import Path

SCRIPT_PATH = Path(sys.argv[0])
SCRIPT_DIR = SCRIPT_PATH.parent
MODULE_DIR = Path(__file__).parent


try:
    import tomli

    with (SCRIPT_DIR / "config/config.toml").open("rb") as file:
        CONFIG = tomli.load(file)

except FileNotFoundError:

    import shutil

    config_dir = SCRIPT_DIR / "config"
    config_dir.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(str(MODULE_DIR / "config_example/minimal.toml"), str(config_dir / "config.toml"))
    shutil.copyfile(str(MODULE_DIR / "config_example/full.toml"), str(config_dir / "config_full_example.toml"))

    CONFIG = {}

required_keys = ['User', 'Database']
for required_key in required_keys:
    if not (CONFIG.__contains__(required_key) and isinstance(CONFIG[required_key], dict)):
        CONFIG[required_key] = {}
