from distutils.core import setup


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


VERSION = find_version('torchvision', '__init__.py')

LONG_DESCRIPTION = open("README.md", 'r').read()

REQUIREMENTS = [
    'requests',
    'pymongo'
]

setup(
    name='stockscreener',
    version=VERSION,
    packages=['stockscreener'],
    author='Oliver Haag',
    url='https://github.com/illoRocks/stockscreener',
    license='Creative Commons Attribution-NonCommercial-ShareAlike 2.0 Germany License',
    long_description=LONG_DESCRIPTION,
    author='Oliver Haag',
    author_email='stockscreener@illo.rocks',
    description='Download XBRL from the SEC and store it to MongoDB or as local files.',
    requires=REQUIREMENTS,
    license='Creative Commons'
)
