import wave
from io import BytesIO


def rebuild(sample, width):
	data = sample.data[:sample.samples * sample.channels * width]
	ret = BytesIO()
	with wave.open(ret, "wb") as wav:
		wav.setparams((sample.channels, width, sample.frequency, 0, "NONE", "NONE"))
		wav.writeframes(data)
	return ret.getvalue()
