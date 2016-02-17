# -*- coding: utf-8 -*-


"""setup.py: setuptools control"""


import sys
import re
from setuptools import setup, find_packages
from subprocess import call
from setuptools.command.install import install


version = re.search(
    '^__version__\s*=\s*"(.*)"',
    open('lyrico/lyrico.py').read(),
    re.M
    ).group(1)


# http://rst.ninjs.org/?n=7fff89b4cadb0bb4bfde3b246d7c1044&theme=basic
with open("README.rst", "rb") as f:
    long_descr = f.read().decode("utf-8")

# Code that runs only during building source distribution.
if sys.argv[1] == 'sdist':
    # 'import' from the pre_sdist module inside the 'if' allows to
    # use any python package safely.
    from pre_sdist import reset_config
    reset_config()
    

# Install dependencies from requirements.txt (install_requires is not working)
# With requirements.txt, win-unicode-console will only be installed for Windows users.
class MyInstall(install):
    def run(self):
        # Call subprocess to run te 'pip' command.
        # Only works, when user installs from sdist
        call(['pip', 'install', '-r', 'requirements.txt'])

        # Run 'install' to install lyrico
        install.run(self)


setup(
    name = "lyrico",
    packages = ["lyrico"],
    entry_points = {
        "console_scripts": ['lyrico = lyrico.lyrico:main']
        },

    cmdclass={'install': MyInstall},

    version = version,
    description = "Download lyrics. Embed lyrics in songs and save to files.",
    long_description = long_descr,
    keywords='lyrics audio foobar2000 tags mp3',
    classifiers=[
        'Development Status :: 3 - Alpha',

        'Intended Audience :: End Users/Desktop',
        'Topic :: Multimedia :: Sound/Audio',

        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',

        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',

        'Operating System :: Microsoft',
        'Operating System :: Unix',
    ],

    author = "Abhimanyu Pathania",
    author_email = "abpindia1944@gmail.com",
    url = "https://github.com/abhimanyuPathania/lyrico",
    license='MIT',

    include_package_data = True,
    package_data = {
        # If any package contains *.ini files, include them:
        '': ['*.ini'],
    },

    )
