#!/usr/bin/env python3

from setuptools import setup, find_packages
import fsb5


setup(
	name='python-fsb5',
	version='1.0',
	author='Simon Pinfold',
	author_email='simon@uint8.me',
	description='Library and to extract audio from FSB5 (FMOD Sample Bank) files',
	download_url='https://github.com/synap5e/python-fsb5/tarball/master',
	license='MIT',
	url='https://github.com/synap5e/python-fsb5',
	packages=find_packages(),
)
