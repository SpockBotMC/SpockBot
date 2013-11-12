import struct
import zlib
from spock import utils
from spock.mcp import mcdata, nbt

#Unpack/Pack functions return None on error

# Minecraft varints are 32-bit signed values
# packed into Google Protobuf varints
def unpack_varint(bbuff):
	total = 0
	shift = 0
	val = 0x80
	while val&0x80:
		val = struct.unpack('B', bbuff.read(1))[0]
		total |= ((val&0x7F)<<shift)
		shift += 7
	if total >= (1<<32):
		return None
	if total&(1<<31):
		total = total - (1<<32)
	return total

def pack_varint(val):
	if val >= (1<<31) or val < -(1<<31):
		return None
	o = b''
	if val < 0:
		val = (1<<32)+val
	while val>=0x80:
		bits = val&0x7F
		val >>= 7
		o += struct.pack('B', (0x80|bits))
	bits = val&0x7F
	o += struct.pack('B', bits)
	return o

# Slots are dictionaries that hold info about
# inventory items, they also have funky
# enchantment data stored in gziped NBT structs
def unpack_slot(bbuff):
	slot = {}
	slot['id'] = unpack('short', bbuff)
	if slot[['id'] != -1:
		slot['amount'] = unpack('byte', bbuff)
		slot['damage'] = unpack('short', bbuff)
		length = unpack('short', bbuff)
		if length > 0:
			data = bbuff.recv(length)
			try:
				ench_bbuff = utils.BoundBuffer(
					#Adding 16 to the window bits field tells zlib
					#to take care of the gzip headers for us
					zlib.decompress(data, 16+zlib.MAX_WBITS)
				)
				assert(unpack('byte', ench_bbuff) == nbt.TAG_COMPOUND)
				name = nbt.TAG_String(buffer = ench_bbuff)
				ench = nbt.TAG_Compound(buffer = ench_bbuff)
				ench.name = name
				slot['enchants'] = ench
			except:
				slot['enchant_data'] = data
	return slot

def pack_slot(slot):
	o = pack('short', data['id'])
	if data['id'] != -1:
		o += pack('byte', data['amount'])
		o += pack('short', data['damage'])
		if 'enchantment_data' in data:
			o += pack('short', len(data['enchant_data']))
			o += data['enchant_data']
		elif 'enchants' in data:
			ench = data['enchants']
			bbuff = utils.BoundBuffer()
			TAG_Byte(ench.id)._render_buffer(bbuff)
			TAG_String(ench.name)._render_buffer(bbuff)
			ench._render_buffer(bbuff)
			#Python zlib.compress doesn't provide wbits for some reason
			#So we'll use a compression object instead, no biggie
			compress = zlib.compressobj(wbits = 16+zlib.MAX_WBITS)
			ench = compress.compress(bbuff.flush())
			ench += compress.flush()
			o += pack('short', len(ench))
			o += ench
		else:
			o += pack('short', -1)
	return o

# Metadata is a dictionary list thing that 
# holds metadata about entities. Currently 
# implemented as a list/tuple thing, might 
# switch to dicts
metadata_lookup = 'byte', 'short', 'int', 'float', 'string', 'slot'

def unpack_metadata(bbuff):
	metadata = []
	head = unpack(bbuff, 'ubyte')
	while head != 127:
		key = head & 0x1F # Lower 5 bits
		typ = head >> 5 # Upper 3 bits
		if typ < len(metadata_lookup) and typ >= 0:
			val = unpack(metadata_lookup[typ], bbuff)
		elif typ == 6:
			val = [unpack(bbuff, 'int') for i in range(3)]
		else:
			return None
		metadata.append((key, (typ, val)))
		head = unpack(bbuff, 'ubyte')
	return metadata

def pack_metadata(metadata):
	o = b''
	for key, tmp in data:
		typ, val = tmp
		o += pack('ubyte', (typ << 5)|key)
		if typ < len(metadata_lookup) and typ >= 0:
			o += pack(metadata_lookup[typ], bbuff)
		elif typ == 6:
			for i in range(3):
				o += pack('int', val[i])
		else:
			return None
	o += pack('byte', 127)
	return o

endian = '>'

def unpack(data_type, bbuff):
	if data_type in mcdata.data_types:
		format = mcdata.data_types[data_type]
		return struct.unpack(endian+format[0], bbuff.recv(format[1]))[0]
	elif data_type == 'string':
		return bbuff.recv(unpack(bbuff, 'short')).decode('utf-8')
	elif data_type == 'varint':
		return unpack_varint(bbuff)
	elif data_type == 'slot':
		return unpack_slot(data)
	elif data_type == 'metadata':
		return unpack_metadata(bbuff)
	else:
		return None

def pack(data_type, data):
	if data_type in mcdata.data_types:
		format = mcdata.data_types[data_type]
		return struct.pack(endian+format[0], data)
	elif data_type == 'string':
		data = data.encode('utf-8')
		return pack('short', len(data)) + data
	elif data_type == 'varint':
		return pack_varint(bbuff)
	elif data_type == 'slot':
		return pack_slot(data)
	elif data_type == 'metadata':
		return pack_metadata(data)
	else:
		return None