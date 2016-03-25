import os
import ctypes
import struct


class BinaryReader:
	def __init__(self, buf, endian="<"):
		self.buf = buf
		self.endian = endian
		self.seek(0, 2)
		self.size = self.tell()
		self.seek(0)

	def read(self, *args):
		return self.buf.read(*args)

	def seek(self, *args):
		return self.buf.seek(*args)

	def tell(self):
		return self.buf.tell()

	def finished(self):
		return self.tell() == self.size

	def read_string(self, maxlen=0):
		r = []
		start = self.tell()
		while maxlen == 0 or len(r) <= maxlen:
			c = self.read(1)
			if not c:
				raise ValueError("Unterminated string starting at %d" % (start))
			if c == b"\0":
				break
			r.append(c)
		return b"".join(r)

	def struct_calcsize(self, fmt):
		return struct.calcsize(fmt)

	def read_struct(self, fmt, endian=None):
		fmt = (endian or self.endian) + fmt;
		fmtlen = struct.calcsize(fmt)
		data = self.read(fmtlen)
		if len(data) != fmtlen:
			raise ValueError("Not enough bytes left in buffer to read struct")
		return struct.unpack(fmt, data)

	def read_struct_into(self, dest, fmt, endian=None):
		fields = self.read_struct(fmt, endian=endian)
		fields = list(fields) + [None] * (len(dest._fields) - len(fields))
		return dest._make(fields)

	def read_type(self, type_fmt, endian=None):
		r = self.read_struct(type_fmt, endian=endian)
		if len(r) != 1:
			raise ValueError("Format %r did not describe a single type" % (type_fmt))
		return r[0]


class LibraryNotFoundException(OSError):
    pass


def load_lib(*names):
	for name in names:
		try:
			libname = ctypes.util.find_library(name)
			if libname:
				return ctypes.CDLL(libname)
			else:
				dll_path = os.path.join(os.getcwd(), "lib%s.dll" % (name))
				return ctypes.CDLL(dll_path)
		except OSError:
			pass
	raise LibraryNotFoundException("Could not load the library %r" % (names[0]))
