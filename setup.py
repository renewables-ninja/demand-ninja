#!/usr/bin/env python

from pathlib import Path
from setuptools import setup, find_packages

exec(Path("demand_ninja/_version.py").read_text())  # Sets the __version__ variable

requirements = Path("requirements.txt").read_text().strip().split("\n")

setup(
    name="demand_ninja",
    version=__version__,
    description="Simulates heating and cooling demand",
    license="BSD-3-Clause",
    packages=find_packages(),
    install_requires=requirements,
    include_package_data=True,
    classifiers=[
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
    ],
)
