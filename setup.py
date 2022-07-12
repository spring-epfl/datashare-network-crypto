import sys
from mspsi import __version__

from setuptools import setup, find_packages

py_version = sys.version_info[:2]
if py_version < (3, 7):
    raise Exception("datashare-network-crypto requires Python >= 3.7.")

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='datashare-network-crypto',
    version=__version__,
    packages=find_packages(),
    description="Crypto primitives for Datashare Network Library",
    use_pipfile=True,
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ICIJ/datashare-network-client",
    setup_requires=['setuptools-pipfile'],
    keywords=['datashare', 'api', 'cryptography'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Operating System :: OS Independent",
        "Topic :: Security :: Cryptography"
    ],
    python_requires='>=3.7',
)
