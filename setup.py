from setuptools import Extension, setup

ext_crypto_path = "aiotieba/client/_crypto/"
ext_module = Extension(
    "aiotieba.client._crypto._crypto",
    sources=[ext_crypto_path + '_crypto.c'],
)

setup(
    name='_crypto',
    ext_modules=[ext_module],
)
