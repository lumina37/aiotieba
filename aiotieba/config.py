# -*- coding:utf-8 -*-
__all__ = ['CONFIG']

from .log import LOG
from .paths import MODULE_DIR, SCRIPT_DIR

try:
    import tomli

    with (SCRIPT_DIR / "config/config.toml").open("rb") as file:
        CONFIG = tomli.load(file)

except FileNotFoundError:

    import shutil

    config_dir = SCRIPT_DIR / "config"
    config_dir.mkdir(parents=True, exist_ok=True)
    minimal_config_path = config_dir / "config.toml"
    shutil.copyfile(str(MODULE_DIR / "config_example/minimal.toml"), str(minimal_config_path))
    shutil.copyfile(str(MODULE_DIR / "config_example/full.toml"), str(config_dir / "config_full_example.toml"))

    CONFIG = {}

    LOG.warning(
        f"找不到配置文件，请参考[https://github.com/Starry-OvO/Tieba-Manager/blob/master/wikis/tutorial.md]完成对{minimal_config_path}的配置"
    )

required_keys = ['User', 'Database']
for required_key in required_keys:
    if required_key not in CONFIG or not isinstance(CONFIG[required_key], dict):
        CONFIG[required_key] = {}
