import ctypes
import ctypes.util
import os
from enum import IntEnum
from io import BytesIO

from . import *
from .utils import BinaryReader, load_lib
from .vorbis_headers import lookup as vorbis_header_lookup


vorbis = load_lib('vorbis')
ogg = load_lib('ogg')


class VorbisInfo(ctypes.Structure):
	"""
	https://xiph.org/vorbis/doc/libvorbis/vorbis_info.html
	"""
	_fields_ = [
		('version', ctypes.c_int),
		('channels', ctypes.c_int),
		('rate', ctypes.c_long),
		('bitrate_upper', ctypes.c_long),
		('bitrate_nominal', ctypes.c_long),
		('bitrate_lower', ctypes.c_long),
		('bitrate_window', ctypes.c_long),
		('codec_setup', ctypes.c_void_p),
	]

	def __init__(self):
		super().__init__()
		vorbis.vorbis_info_init(self)

	def __del__(self):
		vorbis.vorbis_info_clear(self)


class VorbisComment(ctypes.Structure):
	"""
	https://xiph.org/vorbis/doc/libvorbis/vorbis_info.html
	"""
	_fields_ = [
		('user_comments', ctypes.POINTER(ctypes.c_char_p)),
		('comment_lengths', ctypes.POINTER(ctypes.c_int)),
		('comments', ctypes.c_int),
		('vendor', ctypes.c_char_p)
	]

	def __init__(self):
		super().__init__()
		vorbis.vorbis_comment_init(self)

	def __del__(self):
		vorbis.vorbis_comment_clear(self)


class VorbisDSPState(ctypes.Structure):
	"""
	https://svn.xiph.org/trunk/vorbis/include/vorbis/codec.h
	"""
	_fields_ = [
		('analysisp', ctypes.c_int),
		('vi', ctypes.c_void_p),
		('pcm', ctypes.POINTER(ctypes.POINTER(ctypes.c_float))),
		('pcmret', ctypes.POINTER(ctypes.POINTER(ctypes.c_float))),
		('pcm_storage', ctypes.c_int),
		('pcm_current', ctypes.c_int),
		('pcm_returned', ctypes.c_int),
		('preextrapolate', ctypes.c_int),
		('eofflag', ctypes.c_int),
		('lW', ctypes.c_long),
		('W', ctypes.c_long),
		('nW', ctypes.c_long),
		('centerW', ctypes.c_long),
		('granulepos', ctypes.c_longlong),
		('sequence', ctypes.c_longlong),
		('glue_bits', ctypes.c_longlong),
		('time_bits', ctypes.c_longlong),
		('floor_bits', ctypes.c_longlong),
		('res_bits', ctypes.c_longlong),
		('backend_state', ctypes.c_void_p)
	]


class OggStreamState(ctypes.Structure):
	"""
	https://xiph.org/ogg/doc/libogg/ogg_stream_state.html
	"""
	_fields_ = [
		('body_data', ctypes.POINTER(ctypes.c_char)),
		('body_storage', ctypes.c_long),
		('body_fill', ctypes.c_long),
		('body_returned', ctypes.c_long),
		('lacing_vals', ctypes.POINTER(ctypes.c_int)),
		('granule_vals', ctypes.POINTER(ctypes.c_longlong)),
		('lacing_storage', ctypes.c_long),
		('lacing_fill', ctypes.c_long),
		('lacing_packet', ctypes.c_long),
		('lacing_returned', ctypes.c_long),
		('header', ctypes.c_char * 282),
		('header_fill', ctypes.c_int),
		('e_o_s', ctypes.c_int),
		('b_o_s', ctypes.c_int),
		('serialno', ctypes.c_long),
		('pageno', ctypes.c_int),
		('packetno', ctypes.c_longlong),
		('granulepos', ctypes.c_longlong)
	]

	def __init__(self, serialno):
		super().__init__()
		ogg.ogg_stream_init(self, serialno)

	def __del__(self):
		ogg.ogg_stream_clear(self)


class OggPacket(ctypes.Structure):
	"""
	https://xiph.org/ogg/doc/libogg/ogg_packet.html
	"""
	_fields_ = [
		('packet', ctypes.POINTER(ctypes.c_char)),
		('bytes', ctypes.c_long),
		('b_o_s', ctypes.c_long),
		('e_o_s', ctypes.c_long),
		('granulepos', ctypes.c_longlong),
		('packetno', ctypes.c_longlong)
	]

class OggpackBuffer(ctypes.Structure):
	"""
	https://xiph.org/ogg/doc/libogg/oggpack_buffer.html
	"""
	_fields_ = [
		('endbyte', ctypes.c_long),
		('endbit', ctypes.c_int),
		('buffer', ctypes.POINTER(ctypes.c_char)),
		('ptr', ctypes.POINTER(ctypes.c_char)),
		('storage', ctypes.c_long)
	]

	def __init__(self):
		super().__init__()
		ogg.oggpack_writeinit(self)

	def __del__(self):
		ogg.oggpack_writeclear(self)

class OggPage(ctypes.Structure):
	"""
	https://xiph.org/ogg/doc/libogg/oggpack_buffer.html
	"""
	_fields_ = [
		('header', ctypes.POINTER(ctypes.c_char)),
		('header_len', ctypes.c_long),
		('body', ctypes.POINTER(ctypes.c_char)),
		('body_len', ctypes.c_long)
	]

def errcheck(result, func, arguments):
	if result != 0:
		raise OSError('Call to %s(%s) returned %d (error)' % (func.__name__, ', '.join(str(x) for x in arguments), result))
	return result == 0

######## libvorbis functions ########

vorbis.vorbis_info_init.argtypes = [ctypes.POINTER(VorbisInfo)]
vorbis.vorbis_info_init.restype = None

vorbis.vorbis_info_clear.argtypes = [ctypes.POINTER(VorbisInfo)]
vorbis.vorbis_info_clear.restype = None

vorbis.vorbis_comment_init.argtypes = [ctypes.POINTER(VorbisComment)]
vorbis.vorbis_comment_init.restype = None

vorbis.vorbis_comment_clear.argtypes = [ctypes.POINTER(VorbisComment)]
vorbis.vorbis_comment_clear.restype = None

vorbis.vorbis_analysis_init.argtypes = [ctypes.POINTER(VorbisDSPState), ctypes.POINTER(VorbisInfo)]
vorbis.vorbis_analysis_init.errcheck = errcheck

vorbis.vorbis_analysis_headerout.argtypes = [
	ctypes.POINTER(VorbisDSPState),
	ctypes.POINTER(VorbisComment),
	ctypes.POINTER(OggPacket),
	ctypes.POINTER(OggPacket),
	ctypes.POINTER(OggPacket)
]
vorbis.vorbis_analysis_headerout.errcheck = errcheck

vorbis.vorbis_dsp_clear.argtypes = [ctypes.POINTER(VorbisDSPState)]
vorbis.vorbis_dsp_clear.restype = None

vorbis.vorbis_commentheader_out.argtypes = [ctypes.POINTER(VorbisComment), ctypes.POINTER(OggPacket)]
vorbis.vorbis_commentheader_out.errcheck = errcheck

vorbis.vorbis_synthesis_headerin.argtypes = [
	ctypes.POINTER(VorbisInfo),
	ctypes.POINTER(VorbisComment),
	ctypes.POINTER(OggPacket)
]
vorbis.vorbis_synthesis_headerin.errcheck = errcheck


def vorbis_packet_blocksize_errcheck(result, func, arguments):
	if result < 0:
		errcheck(result, func, arguments)
	return result

vorbis.vorbis_packet_blocksize.argtypes = [ctypes.POINTER(VorbisInfo), ctypes.POINTER(OggPacket)]
vorbis.vorbis_packet_blocksize.errcheck = vorbis_packet_blocksize_errcheck


######## libogg functions ########

ogg.ogg_stream_init.argtypes = [ctypes.POINTER(OggStreamState), ctypes.c_int]
ogg.ogg_stream_init.errcheck = errcheck

ogg.ogg_stream_clear.argtypes = [ctypes.POINTER(OggStreamState)]
ogg.ogg_stream_clear.restype = ctypes.c_int

ogg.oggpack_writeinit.argtypes = [ctypes.POINTER(OggpackBuffer)]
ogg.oggpack_writeinit.restype = None

ogg.oggpack_write.argtypes = [ctypes.POINTER(OggpackBuffer), ctypes.c_ulong, ctypes.c_int]
ogg.oggpack_write.restype = None

ogg.oggpack_writeclear.argtypes = [ctypes.POINTER(OggpackBuffer)]
ogg.oggpack_writeclear.restype = None

ogg.oggpack_bytes.argtypes = [ctypes.POINTER(OggpackBuffer)]
ogg.oggpack_bytes.restype = ctypes.c_int

ogg.oggpack_writeclear.argtypes = [ctypes.POINTER(OggpackBuffer)]
ogg.oggpack_writeclear.restype = None

ogg.ogg_packet_clear.argtypes = [ctypes.POINTER(OggPacket)]
ogg.ogg_packet_clear.restype = None

ogg.ogg_stream_packetin.argtypes = [ctypes.POINTER(OggStreamState), ctypes.POINTER(OggPacket)]
ogg.ogg_stream_packetin.errcheck = errcheck

ogg.ogg_stream_pageout.argtypes = [ctypes.POINTER(OggStreamState), ctypes.POINTER(OggPage)]
ogg.ogg_stream_pageout.restype = ctypes.c_int

ogg.ogg_stream_flush.argtypes = [ctypes.POINTER(OggStreamState), ctypes.POINTER(OggPage)]
ogg.ogg_stream_flush.restype = ctypes.c_int

if hasattr(ogg, 'oggpack_writecheck'):
	ogg.oggpack_writecheck.argtypes = [ctypes.POINTER(OggpackBuffer)]
	ogg.oggpack_writecheck.errcheck = errcheck


def rebuild(sample):
	if MetadataChunkType.VORBISDATA not in sample.metadata:
		raise ValueError('Expected sample header to contain a VORBISDATA chunk but none was found')

	crc32 = sample.metadata[MetadataChunkType.VORBISDATA].crc32
	try:
		setup_packet_buff = vorbis_header_lookup[crc32]
	except KeyError as e:
		raise ValueError('Could not find header info for crc32=%d' % crc32) from e

	info = VorbisInfo()
	comment = VorbisComment()
	state = OggStreamState(1)
	outbuf = BytesIO()

	id_header      = rebuild_id_header(sample.channels, sample.frequency, 0x100, 0x800)
	comment_header = rebuild_comment_header()
	setup_header   = rebuild_setup_header(setup_packet_buff)

	vorbis.vorbis_synthesis_headerin(info, comment, id_header)
	vorbis.vorbis_synthesis_headerin(info, comment, comment_header)
	vorbis.vorbis_synthesis_headerin(info, comment, setup_header)

	ogg.ogg_stream_packetin(state, id_header)
	write_packets(state, outbuf)
	ogg.ogg_stream_packetin(state, comment_header)
	write_packets(state, outbuf)
	ogg.ogg_stream_packetin(state, setup_header)
	write_packets(state, outbuf)
	write_packets(state, outbuf, func=ogg.ogg_stream_flush)

	packetno = setup_header.packetno
	granulepos = 0
	prev_blocksize = 0

	inbuf = BinaryReader(BytesIO(sample.data))
	packet_size = inbuf.read_type('H')
	while packet_size:
		packetno += 1

		packet = OggPacket()
		buf = ctypes.create_string_buffer(inbuf.read(packet_size), packet_size)
		packet.packet = ctypes.cast(buf, ctypes.POINTER(ctypes.c_char))
		packet.bytes = packet_size
		packet.packetno = packetno

		try:
			packet_size = inbuf.read_type('H')
		except ValueError:
			packet_size = 0
		packet.e_o_s = 1 if not packet_size else 0

		blocksize = vorbis.vorbis_packet_blocksize(info, packet)
		assert blocksize

		granulepos = int(granulepos + (blocksize + prev_blocksize) / 4) if prev_blocksize else 0
		packet.granulepos = granulepos
		prev_blocksize = blocksize

		ogg.ogg_stream_packetin(state, packet)
		write_packets(state, outbuf)

	return outbuf.getbuffer()


def write_packets(state, buf, func=ogg.ogg_stream_pageout):
	page = OggPage()
	while func(state, page):
		buf.write(bytes(page.header[:page.header_len]))
		buf.write(bytes(page.body[:page.body_len]))


def rebuild_id_header(channels, frequency, blocksize_short, blocksize_long):
	packet = OggPacket()

	buf = OggpackBuffer()
	ogg.oggpack_write(buf, 0x01, 8)
	for c in 'vorbis':
		ogg.oggpack_write(buf, ord(c), 8)
	ogg.oggpack_write(buf, 0, 32)
	ogg.oggpack_write(buf, channels, 8)
	ogg.oggpack_write(buf, frequency, 32)
	ogg.oggpack_write(buf, 0, 32)
	ogg.oggpack_write(buf, 0, 32)
	ogg.oggpack_write(buf, 0, 32)
	ogg.oggpack_write(buf, len(bin(blocksize_short)) - 3, 4)
	ogg.oggpack_write(buf, len(bin(blocksize_long)) - 3, 4)
	ogg.oggpack_write(buf, 1, 1)

	if hasattr(ogg, 'oggpack_writecheck'):
		ogg.oggpack_writecheck(buf)

	packet.bytes = ogg.oggpack_bytes(buf)
	buf = ctypes.create_string_buffer(bytes(buf.buffer[:packet.bytes]), packet.bytes)
	packet.packet = ctypes.cast(ctypes.pointer(buf), ctypes.POINTER(ctypes.c_char))
	packet.b_o_s = 1
	packet.e_o_s = 0
	packet.granulepos = 0
	packet.packetno = 0

	return packet


def rebuild_comment_header():
	packet = OggPacket()
	ogg.ogg_packet_clear(packet)

	comment = VorbisComment()
	vorbis.vorbis_commentheader_out(comment, packet)

	return packet


def rebuild_setup_header(setup_packet_buff):
	packet = OggPacket()

	packet.packet = ctypes.cast(ctypes.pointer(ctypes.create_string_buffer(setup_packet_buff, len(setup_packet_buff))), ctypes.POINTER(ctypes.c_char))
	packet.bytes = len(setup_packet_buff)
	packet.b_o_s = 0
	packet.e_o_s = 0
	packet.granulepos = 0
	packet.packetno = 2

	return packet
