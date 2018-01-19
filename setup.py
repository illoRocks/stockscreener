from distutils.core import setup

setup(
    name='stockscreener',
    version='1.0.0',
    packages=[''],
    url='https://illo.rocks',
    license='Creative Commons Attribution-NonCommercial-ShareAlike 2.0 Germany License',
    author='Oliver Haag',
    author_email='stockscreener@illo.rocks',
    description='Download XBRL from the SEC and store it to MongoDB or as local files.', 
    requires=['requests', 'pymongo']
)
