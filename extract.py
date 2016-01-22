#!/usr/bin/env python3

import argparse
import sys
import os
import fsb5


class FSBExtractor:
	description = 'Extract audio samples from FSB5 files'

	def __init__(self):
		self.parser = self.init_parser()

	def init_parser(self):
		parser = argparse.ArgumentParser(description=self.description)
		parser.add_argument('fsb_file', nargs='*', type=str,
			help='FSB5 container to extract audio from (defaults to stdin)'
		)
		parser.add_argument('-o', '--output-directory', default='out/',
			help='output directory to write extracted samples into'
		)
		parser.add_argument('-p', '--prefix-samples', action='store_true',
			help='prefix extracted samples with the filename of the FSB container they were extracted from'
		)
		parser.add_argument('-q', '--quiet', action='store_true',
			help='suppress most output'
		)
		parser.add_argument('-r', '--resource', action='store_true',
			help="read multiple FSB5 files packed into the same file (e.g. Unity3D's .resource files)"
		)

		return parser

	def print(self, *args):
		if not self.args.quiet:
			print(*args)

	def error(self, *args):
		print(*args, file=sys.stderr)

	def write_to_file(self, filename_prefix, filename, extension, contents):
		directory = self.args.output_directory

		if not os.path.exists(directory):
			os.makedirs(directory)

		if filename_prefix:
			path = os.path.join(directory, '{0}.{1}.{2}'.format(filename_prefix, filename, extension))
		else:
			path = os.path.join(directory, '{0}.{1}'.format(filename, extension))

		with open(path, 'wb') as f:
			written = f.write(contents)
		return path

	def extract_fsb(self, name, data, prefix):
		fsb = fsb5.load(data)
		ext = fsb.get_sample_extension()

		self.print('Header:')
		self.print('\tVersion: 5.%s' % (fsb.header.version))
		self.print('\tSample count: %i' % (fsb.header.numSamples))
		self.print('\tNamed samples: %s' % ('Yes' if fsb.header.nameTableSize else 'No'))
		self.print('\tSound format: %s' % (fsb.header.mode.name.capitalize()))

		failed, written = [], []
		self.print('Samples:')
		for sample in fsb.samples:
			self.print('\t%s.%s' % (sample.name, ext))
			self.print('Frequency: %iHz' % (sample.frequency))
			self.print('Channels: %i' % (sample.channels))
			self.print('Samples %r' % (sample.samples))

			if sample.metadata:
				for meta_type, meta_value in sample.metadata.items():
					if type(meta_type) is fsb5.MetadataChunkType:
						contents = str(meta_value)
						if len(contents) > 45:
							contents = contents[:45] + '... )'
						self.print('\t%s: %s' % (meta_type.name, contents))
					else:
						self.print('\t<unknown metadata type: %r>' % (meta_type))

			sample_fakepath = '{0}:{1}.{2}'.format(name, sample.name, ext)
			try:
				outpath = self.write_to_file(prefix, sample.name, ext, fsb.rebuild_sample(sample))
				written.append((sample_fakepath, outpath))
			except ValueError as e:
				failed.append((sample_fakepath, e))
				self.error(e)

		self.print('\n')

		return failed, written, fsb.raw_size

	def handle_file(self, f):
		data = f.read()
		prefix = os.path.splitext(os.path.basename(f.name))[0] if self.args.prefix_samples else ''

		self.print('Reading FSB5 container: %s' % (f.name))

		if self.args.resource:
			index = 0
			while data:
				nfailed, nwritten, raw_size = self.extract_fsb(
					'{0}:{1}'.format(f.name, index),
					data,
					'{0}.{1}'.format(prefix, index) if prefix else str(index)
				)
				data = data[raw_size:]
				index += 1
		else:
			nfailed, nwritten, _ = self.extract_fsb(f.name, data, prefix)

		return nfailed, nwritten

	def run(self, args):
		self.args = self.parser.parse_args(args)

		failed, written = [], []
		for fname in self.args.fsb_file:
			with open(fname, 'rb') as f:
				nfailed, nwritten = self.handle_file(f)
			failed += nfailed
			written += nwritten

		print('The following files were extracted:')
		for sample_fakepath, outpath in written:
			print('\t' + sample_fakepath, '->', outpath)

		if failed:
			print('The following samples failed to be decoded:')
			for sample_fakepath, reason in failed:
				print('\t' + sample_fakepath, reason)

		return 0

def main():
	app = FSBExtractor()
	exit(app.run(sys.argv[1:]))


if __name__ == '__main__':
	main()
