#!/usr/bin/env python3

import fsb5
from setuptools import setup, find_packages


CLASSIFIERS = [
	"Development Status :: 4 - Beta",
	"Intended Audience :: Developers",
	"License :: OSI Approved :: MIT License",
	"Programming Language :: Python",
	"Programming Language :: Python :: 3",
	"Programming Language :: Python :: 3.4",
	"Programming Language :: Python :: 3.5",
	"Topic :: Multimedia :: Sound/Audio",
	"Topic :: Multimedia :: Sound/Audio :: Conversion",
]


setup(
	name="fsb5",
	version=fsb5.__version__,
	author=fsb5.__author__,
	author_email=fsb5.__email__,
	description="Library and to extract audio from FSB5 (FMOD Sample Bank) files",
	download_url="https://github.com/HearthSim/python-fsb5/tarball/master",
	license="MIT",
	url="https://github.com/HearthSim/python-fsb5",
	classifiers=CLASSIFIERS,
	packages=find_packages(),
)
