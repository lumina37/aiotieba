__all__ = ['CONFIG']

from pathlib import Path

from ._logger import LOG

config_filename = "aiotieba.toml"

try:
    import tomli

    with open(config_filename, "rb") as file:
        CONFIG = tomli.load(file)

except FileNotFoundError:

    import shutil

    module_dir = Path(__file__).parent
    shutil.copyfile(str(module_dir / "config_example/minimal.toml"), config_filename)
    shutil.copyfile(str(module_dir / "config_example/full.toml"), "aiotieba_full_example.toml")

    CONFIG = {}

    LOG.warning(f"配置文件./{config_filename}已生成 请参考注释补充个性化配置")

required_keys = ['User', 'Database']
for required_key in required_keys:
    if required_key not in CONFIG or not isinstance(CONFIG[required_key], dict):
        CONFIG[required_key] = {}
