import struct
import mcdata
import nbt
#from utils import ByteToHex

"""
I want to take a moment to say I really hate all of the code in
this file and it's only a slight step up from a bunch of independent
handler functions. One day, I will figure out a better way to do
this than elif trees.
"""

endian = '>'

def DecodeData(buff, dtype, **kwargs):
	if dtype in mcdata.data_types:
		format = mcdata.data_types[dtype]
		return struct.unpack(endian + format[0], buff.recv(format[1]))[0]

	elif dtype == 'string':
		length = DecodeData(buff, 'short')*2
		return buff.recv(length).decode('utf-16be')

	elif dtype == 'byte_array':
		return buff.recv(kwargs['length'])

	elif dtype == 'slot':
		data = {}
		for field in mcdata.slot:
			if field[0] != 'nbt':
				data[field[1]] = DecodeData(field[0])
			else:
				#Same awful hack we use in Packet
				#Fix when Nick gets a brilliant idea for HOW?!?!?
				data[field[1]] = DecodeData(field[0], length = data[field[1]+'_length'])

		return data

	elif dtype == 'nbt':
		return nbt.decode_nbt(buff.recv(kwargs['length']))

def EncodeData(data, dtype):
	if dtype in mcdata.data_types:
		return struct.pack(endian + mcdata.data_types[dtype][0], data)

	elif dtype == 'string':
		return EncodeData(len(data), 'short') + data.encode("utf-16be")

	elif dtype == 'byte_array':
		return data

	elif dtype == 'slot':
		#Put things here
		pass

	elif dtype == 'nbt':
		#Here too
		pass

