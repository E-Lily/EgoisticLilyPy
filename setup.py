from setuptools import setup

setup(
    name='EgoisticLily',
    version='0.3.0',
    packages=['egoisticlily', 'egoisticlily.proto'],
    install_requires=['torch', 'numpy', 'marisa-trie', 'grpcio-tools', 'tqdm'],
    url='https://github.com/E-Lily/EgoisticLilyPy',
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
