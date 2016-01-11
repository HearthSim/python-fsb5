#!/usr/bin/env python3

import sys
import os
from pprint import pprint
import fsb5

def write_to_file(filename, contents, mode='wb'):
	basedir = 'out'

	if not os.path.exists(basedir):
		os.makedirs(basedir)

	path = os.path.join(basedir, filename)
	with open(path, mode) as f:
		written = f.write(contents)

def main():
	print('Opening {0}'.format(sys.argv[1]))
	with open(sys.argv[1], 'rb') as f:
		fsb = fsb5.load(f.read())

		print('Header:\n\t', fsb.header, '\n')

		print('Samples: ')
		for sample in fsb.samples:
			print('\t"{sample.name}":\n\t\tFrequency: {sample.frequency}\n\t\tChannels: {sample.channels}\n\t\tSamples: {sample.samples}\n\t\tMetadata:'.format(sample=sample))
			for k, v in sample.metadata.items():
				print('\t\t\t{0}: {1}'.format(k, v))

			write_to_file('{0}.{1}'.format(sample.name, fsb.get_sample_extension()), fsb.rebuild_sample(sample))

if __name__ == '__main__':
	main()
