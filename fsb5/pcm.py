import wave
import struct
from io import BytesIO


def rebuild(sample, width):
	data = sample.data[:sample.samples * width]
	ret = BytesIO()
	with wave.open(ret, "wb") as wav:
		wav.setparams((sample.channels, width, sample.frequency, 0, "NONE", "NONE"))
		wav.writeframes(data)
	return ret.getvalue()

def rebuild_float(sample, width):
	data = sample.data[:sample.samples * width]
	ret = BytesIO()
	with PCMFloatWave_write(ret) as wav:
		wav.setparams((sample.channels, width, sample.frequency, 0, "NONE", "NONE"))
		wav.writeframes(data)
	return ret.getvalue()

WAVE_FORMAT_IEEE_FLOAT = 3

class PCMFloatWave_write(wave.Wave_write):
	def _write_header(self, initlength):
		assert not self._headerwritten
		self._file.write(b'RIFF')
		if not self._nframes:
			self._nframes = initlength // (self._nchannels * self._sampwidth)
		self._datalength = self._nframes * self._nchannels * self._sampwidth
		try:
			self._form_length_pos = self._file.tell()
		except (AttributeError, OSError):
			self._form_length_pos = None
		self._file.write(struct.pack('<L4s4sLHHLLHH4s',
		    36 + self._datalength, b'WAVE', b'fmt ', 16,
		    WAVE_FORMAT_IEEE_FLOAT, self._nchannels, self._framerate,
		    self._nchannels * self._framerate * self._sampwidth,
		    self._nchannels * self._sampwidth,
                    self._sampwidth * 8, b'data'))
		if self._form_length_pos is not None:
			self._data_length_pos = self._file.tell()
		self._file.write(struct.pack('<L', self._datalength))
		self._headerwritten = True

