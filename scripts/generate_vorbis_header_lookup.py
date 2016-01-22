#!/usr/bin/env python3

import itertools
import zlib
from pprint import pprint
from fsb5.vorbis import get_header_info


if __name__ == '__main__':
	rates = [8000, 11000, 16000, 22050, 24000, 32000, 44100, 48000]
	lookup = {}
	for quality, channels, rate in itertools.product(range(1, 101), range(1, 3), rates):
		crc32 = zlib.crc32(get_header_info(quality, channels, rate)[2])
		lookup[crc32] = (quality, channels, rate)
	pprint(lookup)
