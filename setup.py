from pathlib import Path

from setuptools import Extension, setup

ext_hash_path = Path("aiotieba/client/_hash")
ext_hash_src_file_in_strs = [str(f) for f in ext_hash_path.glob('*.c')]

third_party_path = Path("3rdparty")
third_party_include_dirs = [
    third_party_path / "base32",
    third_party_path / "crc/crc",
    third_party_path / "WjCryptLib/lib",
    third_party_path / "xxHash",
]
third_party_include_dir_in_strs = [str(d) for d in third_party_include_dirs]


def _yield_file() -> str:
    for include_dir in third_party_include_dirs:
        for f in include_dir.glob('*.c'):
            yield str(f)


third_party_src_file_in_strs = list(_yield_file())

ext_module = Extension(
    "aiotieba.client._hash._hash",
    sources=ext_hash_src_file_in_strs + third_party_src_file_in_strs,
    include_dirs=third_party_include_dir_in_strs,
)

setup(
    name='_hash',
    ext_modules=[ext_module],
)
