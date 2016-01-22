#!/usr/bin/env python3

from setuptools import setup, find_packages
import fsb5


setup(
	name='fsb5',
	version=fsb5.__version__,
	author=fsb5.__author__,
	author_email=fsb5.__email__,
	description='Library and to extract audio from FSB5 (FMOD Sample Bank) files',
	download_url='https://github.com/synap5e/python-fsb5/tarball/master',
	license='MIT',
	url='https://github.com/synap5e/python-fsb5',
	packages=find_packages(),
)
