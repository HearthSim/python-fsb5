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
		parser.add_argument('-r', '--resource', action='store_true',
			help="read multiple FSB5 files packed into the same file (e.g. Unity3D's .resource files)"
		)
		parser.add_argument('--verbose', action='store_true',
			help='be more verbose during extraction'
		)

		return parser

	def print(self, *args):
		print(*args)

	def debug(self, *args):
		if self.args.verbose:
			self.print(*args)

	def error(self, *args):
		print(*args, file=sys.stderr)

	def write_to_file(self, filename_prefix, filename, extension, contents):
		directory = self.args.output_directory

		if not os.path.exists(directory):
			os.makedirs(directory)

		if filename_prefix:
			path = os.path.join(directory, '{0}-{1}.{2}'.format(filename_prefix, filename, extension))
		else:
			path = os.path.join(directory, '{0}.{1}'.format(filename, extension))

		with open(path, 'wb') as f:
			written = f.write(contents)
		return path

	def extract_fsb(self, name, data, prefix):
		fsb = fsb5.load(data)
		ext = fsb.get_sample_extension()

		self.debug('\nHeader:')
		self.debug('\tVersion: 5.%s' % (fsb.header.version))
		self.debug('\tSample count: %i' % (fsb.header.numSamples))
		self.debug('\tNamed samples: %s' % ('Yes' if fsb.header.nameTableSize else 'No'))
		self.debug('\tSound format: %s' % (fsb.header.mode.name.capitalize()))

		self.debug('Samples:')
		for sample in fsb.samples:
			self.debug('\t%s.%s' % (sample.name, ext))
			self.debug('\tFrequency: %iHz' % (sample.frequency))
			self.debug('\tChannels: %i' % (sample.channels))
			self.debug('\tSamples %r' % (sample.samples))

			if sample.metadata and self.args.verbose:
				for meta_type, meta_value in sample.metadata.items():
					if type(meta_type) is fsb5.MetadataChunkType:
						contents = str(meta_value)
						if len(contents) > 45:
							contents = contents[:45] + '... )'
						self.debug('\t%s: %s' % (meta_type.name, contents))
					else:
						self.debug('\t<unknown metadata type: %r>' % (meta_type))

			sample_fakepath = '{0}:{1}.{2}'.format(name, sample.name, ext)
			try:
				outpath = self.write_to_file(prefix, sample.name, ext, fsb.rebuild_sample(sample))
				self.print('%r -> %r' % (sample_fakepath, outpath))
			except ValueError as e:
				self.error('FAILED to extract %r: %s' % (sample_fakepath, e))

			self.debug('')

		return fsb.raw_size

	def handle_file(self, f):
		data = f.read()
		prefix = os.path.splitext(os.path.basename(f.name))[0] if self.args.prefix_samples else ''

		self.debug('Reading FSB5 container: %s' % (f.name))

		if self.args.resource:
			index = 0
			while data:
				raw_size = self.extract_fsb(
					'{0}:{1}'.format(f.name, index),
					data,
					'{0}-{1}'.format(prefix, index) if prefix else str(index)
				)
				data = data[raw_size:]
				index += 1
		else:
			self.extract_fsb(f.name, data, prefix)

	def run(self, args):
		self.args = self.parser.parse_args(args)

		for fname in self.args.fsb_file:
			with open(fname, 'rb') as f:
				self.handle_file(f)

		return 0

def main():
	app = FSBExtractor()
	exit(app.run(sys.argv[1:]))


if __name__ == '__main__':
	main()
