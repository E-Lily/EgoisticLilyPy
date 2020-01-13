from setuptools import setup

setup(
    name='EgoisticLily',
    version='0.2.0',
    packages=['egoisticlily', 'egoisticlily.proto', 'egoisticlily.modelmaker'],
    install_requires=['torch', 'numpy', 'marisa-trie', 'grpcio-tools'],
    url='https://bitbucket.org/egoisticlily/egoisticlily/',
    license='MIT',
    author='Hashimoto Masahiko',
    author_email='hashimom@geeko.jp',
    entry_points={
        "console_scripts": [
            "egoisticlily = egoisticlily.server:main",
        ],
    },
    description=''
)
