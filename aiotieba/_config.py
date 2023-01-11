import sys

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib

_CONFIG_FILENAME = "aiotieba.toml"

try:
    with open(_CONFIG_FILENAME, "rb") as f:
        CONFIG = tomllib.load(f)

except FileNotFoundError:
    CONFIG = {}

required_keys = ['User', 'Database']
for required_key in required_keys:
    if required_key not in CONFIG or not isinstance(CONFIG[required_key], dict):
        CONFIG[required_key] = {}
