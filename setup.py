import pathlib
from distutils.core import setup
from setuptools import setup, find_packages


# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="zotify",
    version="0.6.0",
    author="Zotify",
    description="A music and podcast downloader.",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/team-zotify/zotify.git",
    package_data={'': ['README.md', 'LICENSE']},
    packages=['zotify'],
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'zotify=zotify.__main__:main',
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    install_requires=['ffmpy', 'music_tag', 'Pillow', 'protobuf', 'tabulate', 'tqdm',
                      'librespot @ https://github.com/kokarare1212/librespot-python/archive/refs/heads/rewrite.zip'],
)
