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


extension_dir_str = "./aiotieba/helper/crypto"
extension_dir = Path(extension_dir_str)
include_dir = extension_dir / "include"
source_dir = extension_dir / "src"

print(source_dir)

source_files = glob.glob(str(extension_dir) + '/**/*.c', recursive=True)
print(source_files)


ext_crypto_module = Extension(
    "aiotieba.helper.crypto.crypto",
    sources=source_files,
    include_dirs=[str(include_dir)],
    language='c',
)

setup(
    name='crypto',
    ext_modules=[ext_crypto_module],
    cmdclass={'build_ext': BuildExtension},
)
