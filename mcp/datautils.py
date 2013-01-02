import struct

from utils import ByteToHex
import mcdata

def DecodeData(buff, dtype, **kwargs):
	if dtype in mcdata.data_types:
		format = mcdata.data_types[dtype]
		return struct.unpack('>' + format[0], buff.recv(format[1]))[0]

	elif dtype == 'string':
		length = DecodeData(buff, 'short')*2
		return buff.recv(length).decode('utf-16be')

	elif dtype == 'byte_array':
		return buff.recv(kwargs['length'])

	elif dtype == 'slot':
		pass

def EncodeData(data, dtype):
	if dtype in mcdata.data_types:
		return struct.pack('>' + mcdata.data_types[dtype][0], data)

	elif dtype == 'string':
		return EncodeData(len(data), 'short') + data.encode("utf-16be")

	elif dtype == 'byte_array':
		return data

	elif dtype == 'slot':
		pass