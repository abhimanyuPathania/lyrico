# -*- coding: utf-8 -*-


"""setup.py: setuptools control. Only build using Python27"""


import re
from setuptools import setup, find_packages


version = re.search(
    '^__version__\s*=\s*"(.*)"',
    open('lyrico/lyrico.py').read(),
    re.M
    ).group(1)


with open("README.rst", "rb") as f:
    long_descr = f.read().decode("utf-8")


setup(
    name = "lyrico",
    packages = ["lyrico"],
    entry_points = {
        "console_scripts": ['lyrico = lyrico.lyrico:main']
        },

    version = version,
    description = "Download and save lyrics to the song's tag and text file.",
    long_description = long_descr,
    keywords='lyrics, audio, tags',
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: End Users/Desktop',
        'Topic :: Multimedia :: Sound/Audio',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',

        'Operating System :: Microsoft',
    ],

    author = "Abhimanyu Pathania",
    author_email = "abpindia1944@gmail.com",
    url = "https://github.com/abhimanyuPathania/lyrico",
    license='MIT',

    install_requires = [
        'mutagen',
        'glob2',
        'beautifulsoup4',
        'win-unicode-console'
    ],

    include_package_data = True,
    package_data = {
        # If any package contains *.ini files, include them:
        '': ['*.ini'],
    },

    )
