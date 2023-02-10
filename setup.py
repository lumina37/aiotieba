from pathlib import Path

from setuptools import Extension, setup

third_party_path = Path("3rdparty")
ext_path = Path("aiotieba/client/_crypto")
ext_src_in_strs = [str(f) for f in ext_path.glob('*.c')]

ext_3rdparty_include_dirs = [
    third_party_path,
    third_party_path / "mbedtls/library",
    third_party_path / "mbedtls/include",
    third_party_path / "base32",
    third_party_path / "crc",
    third_party_path / "xxHash",
    third_party_path / "rapidjson/internal",
]
ext_3rdparty_include_in_strs = [str(d) for d in ext_3rdparty_include_dirs]


def _yield_file() -> str:
    for include_dir in ext_3rdparty_include_dirs:
        for f in include_dir.glob('*.c'):
            yield str(f)


ext_3rdparty_src_in_strs = list(_yield_file())

ext_crypto_module = Extension(
    "aiotieba.client._crypto.crypto",
    sources=ext_src_in_strs + ext_3rdparty_src_in_strs,
    include_dirs=ext_3rdparty_include_in_strs,
    language='c',
)

setup(
    name='crypto',
    ext_modules=[ext_crypto_module],
)
