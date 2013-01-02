import struct

from utils import ByteToHex
import mcdata

def DecodeData(data, dtype, **kwargs):
	if 'length' in kwargs:
		length = kwargs['length']

	if dtype in mcdata.data_types:
		length = mcdata.data_types[dtype][1]
		return (struct.unpack('>' + mcdata.data_types[dtype][0], data[:length])[0], data[length:])

	elif dtype == 'string':
		data = DecodeData(data, 'short')
		length = data[0]*2
		return (data[1][:length].decode("utf-16be"), data[1][length:])

	elif dtype == 'byte_array':
		return (data[:length], data[length:])

	elif dtype == 'slot':
		pass

def DecodePacket(packet, direction=mcdata.SERVER_TO_CLIENT):
	data = DecodeData(packet, 'ubyte')
	packetid, packet = data[0], data[1]
	if packetid in mcdata.structs:
		decodedpacket = {}
		for field in mcdata.structs[packetid][direction]:
			if field[0] in mcdata.data_types or field[0] == 'string':
				data = DecodeData(packet, field[0])
			elif field[0] == 'byte_array':
				#Cheap shortcut used to get byte_array length, will almost certainly break in the future, fix this
				data = DecodeData(packet, field[0], length = decodedpacket[field[1]+'_length'])
				
			decodedpacket[field[1]], packet = data[0], data[1]

		return decodedpacket
	else:
		print "Something fucked up decoding packets"

def EncodeData(data, dtype):
	if dtype in mcdata.data_types:
		return struct.pack('>' + mcdata.data_types[dtype][0], data)

	elif dtype == 'string':
		return EncodeData(len(data), 'short') + data.encode("utf-16be")

	elif dtype == 'byte_array':
		return data

	elif dtype == 'slot':
		pass

def EncodePacket(data, packetid, direction=mcdata.CLIENT_TO_SERVER):
	out = ''
	if packetid in mcdata.structs:
		for field in mcdata.structs[packetid][direction]:
				out += EncodeData(data[field[1]], field[0])
		return out
	else:
		print "Something fucked up encoding packets"