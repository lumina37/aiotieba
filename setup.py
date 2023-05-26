from pathlib import Path

from setuptools import Extension, setup
from setuptools.command.build_ext import build_ext

third_party_path = Path("thirdparty")
ext_path = Path("aiotieba/helper/crypto")
ext_src_in_strs = [str(f) for f in ext_path.glob('*.c')]

ext_thirdparty_include_dirs = [
    third_party_path,
    third_party_path / "mbedtls/include",
]
ext_thirdparty_include_in_strs = [str(d) for d in ext_thirdparty_include_dirs]
ext_thirdparty_src_dirs = [
    third_party_path,
    third_party_path / "mbedtls/library",
    third_party_path / "base32",
    third_party_path / "crc",
    third_party_path / "xxHash",
]


def _yield_file() -> str:
    for src_dir in ext_thirdparty_src_dirs:
        for f in src_dir.glob('*.c'):
            yield str(f)


ext_thirdparty_src_in_strs = list(_yield_file())


class BuildExtension(build_ext):
    def build_extensions(self):
        if self.compiler.compiler_type == 'msvc':
            opts = ['/Wall']
        else:
            opts = ['-Wextra', '-Wpedantic']
        for ext in self.extensions:
            ext.extra_compile_args = opts
        build_ext.build_extensions(self)


ext_crypto_module = Extension(
    "aiotieba.helper.crypto.crypto",
    sources=ext_src_in_strs + ext_thirdparty_src_in_strs,
    include_dirs=ext_thirdparty_include_in_strs,
    language='c',
)

setup(
    name='crypto',
    ext_modules=[ext_crypto_module],
    cmdclass={'build_ext': BuildExtension},
)
