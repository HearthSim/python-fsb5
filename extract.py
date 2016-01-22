#!/usr/bin/env python3

import argparse
import sys
import os
import fsb5

parser = argparse.ArgumentParser(description='Extract audio samples from FSB5 files')
parser.add_argument('fsb_file', nargs='*', type=argparse.FileType('rb'), default=[sys.stdin.buffer.raw ],
						help='FSB5 container to extract audio from (defaults to stdin)')
parser.add_argument('-o', '--output-directory', default='out',
						help='output directory to write extracted samples into')
parser.add_argument('-p', '--prefix-samples', action='store_true',
						help='prefix extracted samples with the filename of the FSB container they were extracted from')
parser.add_argument('-q', '--quiet', action='store_true',
						help='suppress output of header and sample information (samples that failed to decode will still be printed)')
parser.add_argument('-r', '--resource', action='store_true',
						help='read multiple FSB5 files packed into the same file (e.g. Unity3D\'s .resource files)')

def write_to_file(directory, filename_prefix, filename, extension, contents):
	if not os.path.exists(directory):
		os.makedirs(directory)

	if filename_prefix:
		path = os.path.join(directory, '{0}.{1}.{2}'.format(filename_prefix, filename, extension))
	else:
		path = os.path.join(directory, '{0}.{1}'.format(filename, extension))

	with open(path, 'wb') as f:
		written = f.write(contents)
	return path

def extract_fsb(name, data, prefix, output_directory, printq):
	fsb = fsb5.load(data)
	ext = fsb.get_sample_extension()

	printq('''Header:
	Version: 5.{header.version}
	Number of samples: {header.numSamples}
	Samples have names: {has_names}
	Sound format: {sound_format}'''.format(
		header=fsb.header,
		has_names='Yes' if fsb.header.nameTableSize else 'No',
		sound_format=fsb.header.mode.name.lower().capitalize()))

	failed, written = [], []
	printq('Samples: ')
	for sample in fsb.samples:
		printq('''\t{sample.name}.{extension}:
		Frequency: {sample.frequency}
		Channels: {sample.channels}
		Samples: {sample.samples}'''.format(sample=sample, extension=ext))
		if sample.metadata:
			for meta_type, meta_value in sample.metadata.items():
				if type(meta_type) is fsb5.MetadataChunkType:
					contents = str(meta_value)
					if len(contents) > 45:
						contents = contents[:45] + '... )'
					printq('\t\t{type}: {contents}'.format(type=meta_type.name, contents=contents))
				else:
					printq('\t\t<unknown metadata type: {0}'.format(meta_type))

		sample_fakepath = '{0}:{1}.{2}'.format(name, sample.name, ext)
		try:
			outpath = write_to_file(output_directory, prefix, sample.name, ext, fsb.rebuild_sample(sample))
			written.append((sample_fakepath, outpath))
		except ValueError as e:
			failed.append((sample_fakepath, e))
			printq(e)
	printq()
	printq()

	return failed, written, fsb.raw_size

def main():
	args = parser.parse_args()
	if args.fsb_file[0].fileno() == 0 and args.prefix_samples:
		parser.error('Cannot prefix samples with filename when input is stdin')
	def printq(*a):
		if args.quiet:
			return
		else:
			print(*a)

	failed, written = [], []
	for f in args.fsb_file:
		data = f.read()
		prefix = os.path.splitext(os.path.basename(f.name))[0] if args.prefix_samples else ''

		printq('Reading FSB5 container: {0}'.format(f.name))

		if args.resource:
			index = 0
			while data:
				nfailed, nwritten, raw_size = extract_fsb(
					'{0}:{1}'.format(f.name, index),
					data,
					'{0}.{1}'.format(prefix, index) if prefix else str(index),
					args.output_directory,
					printq
				)
				data = data[raw_size:]
				index += 1
				failed += nfailed
				written += nwritten
		else:
			nfailed, nwritten, _ = extract_fsb(f.name, data, prefix, args.output_directory, printq)
			failed += nfailed
			written += nwritten

	print('The following filed were extracted:')
	for sample_fakepath, outpath in written:
		print('\t' + sample_fakepath, '->', outpath)

	if failed:
		print('The following samples failed to be decoded:')
		for sample_fakepath, reason in failed:
			print('\t' + sample_fakepath, reason)


if __name__ == '__main__':
	main()
