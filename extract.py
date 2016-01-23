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

	def load_fsb(self, data):
		fsb = fsb5.load(data)
		ext = fsb.get_sample_extension()

		self.debug('\nHeader:')
		self.debug('\tVersion: 5.%s' % (fsb.header.version))
		self.debug('\tSample count: %i' % (fsb.header.numSamples))
		self.debug('\tNamed samples: %s' % ('Yes' if fsb.header.nameTableSize else 'No'))
		self.debug('\tSound format: %s' % (fsb.header.mode.name.capitalize()))

		return fsb, ext

	def read_samples(self, fsb_name, fsb, ext):
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

			sample_fakepath = '{0}:{1}.{2}'.format(fsb_name, sample.name, ext)
			try:
				yield sample_fakepath, sample.name, fsb.rebuild_sample(sample)
			except ValueError as e:
				self.error('FAILED to extract %r: %s' % (sample_fakepath, e))

	def handle_file(self, f):
		data = f.read()
		fsb_name = os.path.splitext(os.path.basename(f.name))[0]

		self.debug('Reading FSB5 container: %s' % (f.name))

		is_resource = False
		index = 0
		while data:
			fsb, ext = self.load_fsb(data)

			data = data[fsb.raw_size:]
			if not is_resource and data:
				is_resource = True

			sample_prefix = fsb_name
			fakepath_prefix = fsb_name
			if is_resource:
				sample_prefix += '-%d' % (index)
				fakepath_prefix += ':%d' % (index)
			for sample_fakepath, sample_name, sample_data in self.read_samples(fakepath_prefix, fsb, ext):
				outpath = self.write_to_file(sample_prefix, sample_name, ext, sample_data)
				self.print('%r -> %r' % (sample_fakepath, outpath))

			index += 1

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
