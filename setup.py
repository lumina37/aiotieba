import glob
from pathlib import Path

from setuptools import Extension, setup
from setuptools.command.build_ext import build_ext


class BuildExtension(build_ext):
    def build_extensions(self):
        if self.compiler.compiler_type == 'msvc':
            opts = ['/Wall']
        else:
            opts = ['-Wextra', '-Wpedantic']
        for ext in self.extensions:
            ext.extra_compile_args = opts
        build_ext.build_extensions(self)


extension_dir = Path("./aiotieba/helper/crypto")
include_dir = extension_dir / "include"
source_dir = extension_dir / "src"

source_files = glob.glob(f"{extension_dir}/**/*.c", recursive=True)

ext_crypto_module = Extension(
    "aiotieba.helper.crypto.crypto",
    sources=source_files,
    include_dirs=[str(include_dir)],
    define_macros=[('TBC_NO_CHECK', None)],
    language='c',
)

setup(
    name='crypto',
    ext_modules=[ext_crypto_module],
    cmdclass={'build_ext': BuildExtension},
)
