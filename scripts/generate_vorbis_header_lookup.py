#!/usr/bin/env python3

import argparse
import pefile
import struct
from pprint import pprint


def main():
	pp = argparse.ArgumentParser(description='Dump FSB5 vorbis headers from a 32-bit Windows executable')
	pp.add_argument('file', help='path to executable file')
	args = pp.parse_args()
	pe = pefile.PE(args.file)
	lookup = {}
	base_addr = pe.OPTIONAL_HEADER.ImageBase

	# reimplementation of get_memory_mapped_image because pefile did not survive
	# the port to python 3 fully in tact...
	mapped_data = pe.__data__[:]
	for section in pe.sections:

		# Miscellaneous integrity tests.
		# Some packer will set these to bogus values to make tools go nuts.
		if section.Misc_VirtualSize == 0 or section.SizeOfRawData == 0:
			continue

		if section.SizeOfRawData > len(pe.__data__):
			continue

		if pe.adjust_FileAlignment( section.PointerToRawData,
			pe.OPTIONAL_HEADER.FileAlignment ) > len(pe.__data__):

			continue

		VirtualAddress_adj = pe.adjust_SectionAlignment( section.VirtualAddress,
			pe.OPTIONAL_HEADER.SectionAlignment, pe.OPTIONAL_HEADER.FileAlignment )

		padding_length = VirtualAddress_adj - len(mapped_data)

		if padding_length>0:
			mapped_data += b'\0'*padding_length
		elif padding_length<0:
			mapped_data = mapped_data[:padding_length]

		mapped_data += section.get_data()

	vas = []
	va = 0
	while True:
		va = mapped_data.find(b'\x05vorbis', va)
		if va > 0:
			vas.append(base_addr + va)
			va += 7
		else:
			break

	refs = []
	for va in vas:
		word = struct.pack('<I', va)
		ref = 0
		while True:
			ref = mapped_data.find(word, ref)
			if ref > 0:
				refs.append(base_addr + ref)
				ref += 4
			else:
				break
	refs.sort()

	table_addr = 0
	for ref in refs:
		if (ref - 24 not in refs and ref - 12 not in refs) and (ref + 24 in refs or ref + 36 in refs):
			table_addr = ref
			break

	if table_addr == 0:
		raise

	ea = table_addr
	while True:
		ea_ofs = ea - base_addr
		buf1, len1, crc, buf2, ofs, len2 = struct.unpack('<IIIIII', mapped_data[ea_ofs:ea_ofs+0x18])
		if crc == 0 or len1 == 0 or buf1 == 0 or len1 > 8192 or len2 > 8192:
			break
		hdr = bytearray(len1)
		base_buf = buf1
		if buf2 != 0:
			base_buf = buf2
		for j in range(len1):
			hdr[j] = mapped_data[base_buf + j - base_addr]
		if buf2 != 0:
			for j in range(len2):
				hdr[ofs+j] = mapped_data[buf1 + j - base_addr]
		lookup[crc] = bytes(hdr)
		ea += 24
	print('lookup = ', end='')
	pprint(lookup)


if __name__ == '__main__':
	main()
