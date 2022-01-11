"""A setuptools based setup module.
See:
https://packaging.python.org/guides/distributing-packages-using-setuptools/
https://github.com/pypa/sampleproject
Modified by Madoshakalaka@Github (dependency links added)
"""

from setuptools import setup, find_packages
from os import path
from io import open

here = path.abspath(path.dirname(__file__))

with open(path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="obyde",
    version="0.2.0",
    description="A simple tool to convert a collection of markdown notes to Jekyll or Hugo posts. Mainly aimed at Obsidian vaults.",
    long_description_content_type="text/markdown",
    url="https://github.com/khalednassar/obyde",
    author="Khaled Nassar",
    packages=find_packages(exclude=["contrib", "docs", "tests"]),
    python_requires=">=3.8",
    install_requires=["python-frontmatter==1.0.0", "pyyaml==6.0"],
    dependency_links=[],
    entry_points={"console_scripts": ["obyde=obyde:main"]},
)
