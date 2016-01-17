from collections import namedtuple
from enum import IntEnum
from io import BytesIO

from .utils import BinaryReader


class SoundFormat(IntEnum):
	NONE = 0
	PCM8 = 1
	PCM16 = 2
	PCM24 = 3
	PCM32 = 4
	PCMFLOAT = 5
	GCADPCM = 6
	IMAADPCM = 7
	VAG = 8
	HEVAG = 9
	XMA = 10
	MPEG = 11
	CELT = 12
	AT9 = 13
	XWMA = 14
	VORBIS = 15

file_extensions = {
	SoundFormat.MPEG     : 'mp3',
	SoundFormat.VORBIS   : 'ogg'
}

FSB5Header = namedtuple('FSB5Header',
	[	'id',
		'version',
		'numSamples',
		'sampleHeadersSize',
		'nameTableSize',
		'dataSize',
		'mode',

		'zero',
		'hash',
		'dummy',

		'unknown',

		'size'
	])

Sample = namedtuple('Sample',
	[	'name',
		'frequency',
		'channels',
		'dataOffset',
		'samples',

		'metadata',

		'data'
	])

frequency_values = {
	1: 8000,
	2: 11000,
	3: 11025,
	4: 16000,
	5: 22050,
	6: 24000,
	7: 32000,
	8: 44100,
	9: 48000
}

class MetadataChunkType(IntEnum):
	CHANNELS=1
	FREQUENCY=2
	LOOP=3
	XMASEEK=6
	DSPCOEFF=7
	XWMADATA=10
	VORBISDATA=11

chunk_data_format = {
	MetadataChunkType.CHANNELS : 'B',
	MetadataChunkType.FREQUENCY: 'I',
	MetadataChunkType.LOOP: 'II'
}

VorbisData = namedtuple('VorbisData', ['crc32', 'unknown'])


def bits(val, start, len):
	stop = start + len
	r = val & ((1<<stop)-1)
	return r >> start


class FSB5():
	def __init__(self, data):
		buf = BinaryReader(BytesIO(data), endian='<')

		magic = buf.read(4)
		if magic != b'FSB5':
			raise ValueError('Expected magic header \'FSB5\' but got %r' % (magic))

		buf.seek(0)
		self.header = buf.read_struct_into(FSB5Header, '4s I I I I I I 8s 16s 8s')
		if self.header.version == 0:
			self.header = self.header._replace(unknown=buf.read_type('I'))
		self.header = self.header._replace(mode=SoundFormat(self.header.mode), size=buf.tell())

		self.samples = []
		for i in range(self.header.numSamples):
			raw = buf.read_type('Q')
			next_chunk  = bits(raw, 0,        1)
			frequency   = bits(raw, 1,        4)
			channels    = bits(raw, 1+4,      1)  + 1
			dataOffset 	= bits(raw, 1+4+1,    28) * 16
			samples     = bits(raw, 1+4+1+28, 30)

			frequency = frequency_values[frequency]

			chunks = {}
			while next_chunk:
				raw = buf.read_type('I')
				next_chunk = bits(raw, 0,    1)
				chunk_size = bits(raw, 1,    24)
				chunk_type = bits(raw, 1+24, 7)

				try:
					chunk_type = MetadataChunkType(chunk_type)
				except ValueError:
					pass
				if chunk_type == MetadataChunkType.VORBISDATA:
					chunk_data = VorbisData(
						crc32   = buf.read_type('I'),
						unknown = buf.read(chunk_size-4)
					)
				elif chunk_type in chunk_data_format:
					fmt = chunk_data_format[chunk_type]
					assert buf.struct_calcsize(fmt) == chunk_size, 'Expected chunk %s to be of size %d, but SampleHeader specified %d' % \
																	(chunk_type, buf.struct_calcsize(fmt), chunk_size)
					chunk_data = buf.read_struct(fmt)
				else:
					chunk_data = buf.read(chunk_size)

				chunks[chunk_type] = chunk_data

			self.samples.append(Sample(
				name 		= '%04d' % i,
				frequency 	= frequency,
				channels 	= channels,
				dataOffset 	= dataOffset,
				samples 	= samples,

				metadata=chunks,

				data=None
			))


		if self.header.nameTableSize:
			nametable_start = buf.tell()

			samplename_offsets = []
			for i in range(self.header.numSamples):
				samplename_offsets.append(buf.read_type('I'))

			for i in range(self.header.numSamples):
				buf.seek(nametable_start + samplename_offsets[i])
				name = buf.read_string(maxlen=self.header.nameTableSize)
				self.samples[i] = self.samples[i]._replace(name=name.decode('utf-8'))

		buf.seek(self.header.size + self.header.sampleHeadersSize + self.header.nameTableSize)
		for i in range(self.header.numSamples):
			data_start = self.samples[i].dataOffset
			data_end   = buf.size
			if i < self.header.numSamples-1:
				data_end = self.samples[i+1].dataOffset
			self.samples[i] = self.samples[i]._replace(data=buf.read(data_end - data_start))

	def rebuild_sample(self, sample):
		if sample not in self.samples:
			raise ValueError('Sample to decode did not originate from the FSB archive decoding it')
		if self.header.mode == SoundFormat.MPEG:
			return sample.data
		elif self.header.mode == SoundFormat.VORBIS:
			# import here as vorbis.py requires native libraries
			from . import vorbis
			return vorbis.rebuild(sample)
		else:
			raise NotImplementedError('Decoding samples of type %s is not supported' % self.header.mode)

	def get_sample_extension(self):
		return file_extensions.get(self.header.mode, 'bin')


def load(data):
	return FSB5(data)
