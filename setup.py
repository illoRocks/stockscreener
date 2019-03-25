from setuptools import setup, find_packages
from os import read
import re


def find_version(file_paths):
    version_file = open("stockscreener/__init__.py", 'r').read()
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


VERSION = find_version('stockscreener/__init__.py')

LONG_DESCRIPTION = open("README.md", 'r').read()

REQUIREMENTS = [
    'requests',
    'pymongo',
    'aiohttp',
    'sshtunnel',
    'ConfigArgParse'
]

setup(
    name='stockscreener',
    version=VERSION,
    packages=find_packages(),
    author='Oliver Haag',
    author_email='stockscreener@illo.rocks',
    url='https://github.com/illoRocks/stockscreener',
    license='Creative Commons Attribution-NonCommercial-ShareAlike 2.0 Germany License',
    long_description=LONG_DESCRIPTION,
    description='Download XBRL from the SEC and store it to MongoDB or as local files.',
    install_requires=REQUIREMENTS
)

# sudo python3 setup.py install --record files.txt
# cat files.txt | xargs sudo rm -rf && sudo rm files.txt
