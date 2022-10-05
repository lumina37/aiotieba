__all__ = ['CONFIG']

import sys

from ._logger import LOG

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib

_CONFIG_FILENAME = "aiotieba.toml"


try:
    with open(_CONFIG_FILENAME, "rb") as f:
        CONFIG = tomllib.load(f)

except FileNotFoundError:

    import importlib.resources

    files = importlib.resources.files(__package__) / 'config_example'

    with open(_CONFIG_FILENAME, 'wb') as f:
        f.write((files / "min.toml").read_bytes())
    with open("aiotieba_full_example.toml", 'wb') as f:
        f.write((files / "full.toml").read_bytes())

    CONFIG = {}

    LOG.warning(f"配置文件./{_CONFIG_FILENAME}已生成 请参考注释补充个性化配置")

required_keys = ['User', 'Database']
for required_key in required_keys:
    if required_key not in CONFIG or not isinstance(CONFIG[required_key], dict):
        CONFIG[required_key] = {}
