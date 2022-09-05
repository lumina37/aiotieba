__all__ = ['CONFIG']

from pathlib import Path

from ._logger import LOG

_CONFIG_FILENAME = "aiotieba.toml"

try:
    import tomli

    with open(_CONFIG_FILENAME, "rb") as file:
        CONFIG = tomli.load(file)

except FileNotFoundError:

    import shutil

    module_dir = Path(__file__).parent
    shutil.copyfile(str(module_dir / "config_example/min.toml"), _CONFIG_FILENAME)
    shutil.copyfile(str(module_dir / "config_example/full.toml"), "aiotieba_full_example.toml")

    CONFIG = {}

    LOG.warning(f"配置文件./{_CONFIG_FILENAME}已生成 请参考注释补充个性化配置")

required_keys = ['User', 'Database']
for required_key in required_keys:
    if required_key not in CONFIG or not isinstance(CONFIG[required_key], dict):
        CONFIG[required_key] = {}
