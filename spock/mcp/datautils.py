import struct
import mcdata
import nbt
from utils import ByteToHex

endian = '>'

def unpack(bbuff, data_type):
	if data_type in mcdata.data_types:
		format = mcdata.data_types[data_type]
		return struct.unpack(endian+format[0], bbuff.recv(format[1]))[0]
	
	if data_type == "string":
		length = unpack(bbuff, 'short')
		return bbuff.recv(2*length).decode('utf-16be')

	if data_type == "slot":
		o = {}
		o["id"] = unpack(bbuff, 'short')
		if o["id"] > 0:
			o["amount"] = unpack(bbuff, 'byte')
			o["damage"] = unpack(bbuff, 'short')
			#if o['id'] in enchantable:
			length = unpack(bbuff, 'short')
			if length > 0:
				ench = bbuff.recv(length)
				try:
					ench = nbt.decode_nbt(ench)
					o["enchantments"] = ench
				except:
					o["enchantment_data"] = ench
		return o

	if data_type == "metadata":
		metadata = []
		x = unpack(bbuff, 'ubyte')
		while x != 127:
			key = x & 0x1F # Lower 5 bits
			ty = x >> 5 # Upper 3 bits
			if ty == 0: val = unpack(bbuff, 'byte')
			if ty == 1: val = unpack(bbuff, 'short')
			if ty == 2: val = unpack(bbuff, 'int')
			if ty == 3: val = unpack(bbuff, 'float')
			if ty == 4: val = unpack(bbuff, 'string16')
			if ty == 5:
				val = {}
				val["id"] = unpack(bbuff, 'short')
				val["count"] = unpack(bbuff, 'byte')
				val["damage"] = unpack(bbuff, 'short')
			if ty == 6:
				val = []
				for i in range(3):
					val.append(unpack(bbuff, 'int'))
			metadata.append((key, (ty, val)))
			x = unpack(bbuff, 'byte')
		return metadata

def pack(data_type, data):
	if data_type in mcdata.data_types:
		format = mcdata.data_types[data_type]
		return struct.pack(endian+format[0], data)
	
	if data_type == "string":
		return pack("short", len(data)) + data.encode('utf-16be')

	if data_type == "slot":
		o = pack('short', data['id'])
		if data['id'] > 0:
			o += pack('byte', data['amount'])
			o += pack('short', data['damage'])
			#if data['id'] in enchantable:
			if 'enchantment_data' in data:

				o += pack('short', len(data['enchantment_data']))
				o += data['enchantment_data']

			elif 'enchantments' in data:
				ench = nbt.encode_nbt(data['enchantments'])
				o += pack('short', len(ench))
				o += ench
			else:
				o += pack('short', -1)
				
		return o
	if data_type == "metadata":
		o = ''
		for key, tmp in data:
			ty, val = tmp
			x = key | (ty << 5)
			o += pack('ubyte', x)

			if ty == 0: o += pack('byte', val)
			if ty == 1: o += pack('short', val)
			if ty == 2: o += pack('int', val)
			if ty == 3: o += pack('float', val)
			if ty == 4: o += pack('string16', val)
			if ty == 5:
				o += pack('short', val['id'])
				o += pack('byte', val['count'])
				o += pack('short', val['damage'])
			if ty == 6:
				for i in range(3):
					o += pack('int', val[i])
		o += pack('byte', 127)
		return o

def unpack_array(bbuff, data_type, count):
	#fast
	if data_type in mcdata.data_types:
		data_type = mcdata.data_types[data_type]
		length = data_type[1] * count
		format = data_type[0] * count
		return struct.unpack_from(format, bbuff.recv(length))
	#slow
	else:
		a = []
		for i in range(count):
			a.append(unpack(bbuff, data_type))
		return a

def pack_array(data_type, data):
	#fast
	if data_type in mcdata.data_types:
		data_type = mcdata.data_types[data_type]
		return struct.pack(data_type[0]*len(data), *data)
	#slow
	else:
		o = ''
		for d in data:
			o += pack(data_type, d)
		return o