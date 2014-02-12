import struct
import zlib
from spock import utils
from spock.mcp import mcdata, nbt
from spock.mcp.mcdata import (
	MC_BOOL, MC_UBYTE, MC_BYTE, MC_USHORT, MC_SHORT, MC_UINT, MC_INT,
	MC_LONG, MC_FLOAT, MC_DOUBLE, MC_STRING, MC_VARINT, MC_SLOT, MC_META
)

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
	slot['id'] = unpack(MC_SHORT, bbuff)
	if slot['id'] != -1:
		slot['amount'] = unpack(MC_BYTE, bbuff)
		slot['damage'] = unpack(MC_SHORT, bbuff)
		length = unpack(MC_SHORT, bbuff)
		if length > 0:
			data = bbuff.recv(length)
			try:
				ench_bbuff = utils.BoundBuffer(
					#Adding 16 to the window bits field tells zlib
					#to take care of the gzip headers for us
					zlib.decompress(data, 16+zlib.MAX_WBITS)
				)
				assert(unpack(MC_BYTE, ench_bbuff) == nbt.TAG_COMPOUND)
				name = nbt.TAG_String(buffer = ench_bbuff)
				ench = nbt.TAG_Compound(buffer = ench_bbuff)
				ench.name = name
				slot['enchants'] = ench
			except:
				slot['enchant_data'] = data
	return slot

def pack_slot(slot):
	o = pack(MC_SHORT, data['id'])
	if data['id'] != -1:
		o += pack(MC_BYTE, data['amount'])
		o += pack(MC_SHORT, data['damage'])
		if 'enchantment_data' in data:
			o += pack(MC_SHORT, len(data['enchant_data']))
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
			o += pack(MC_SHORT, len(ench))
			o += ench
		else:
			o += pack(MC_SHORT, -1)
	return o

# Metadata is a dictionary list thing that 
# holds metadata about entities. Currently 
# implemented as a list/tuple thing, might 
# switch to dicts
metadata_lookup = MC_BYTE, MC_SHORT, MC_INT, MC_FLOAT, MC_STRING, MC_SLOT

def unpack_metadata(bbuff):
	metadata = []
	head = unpack(MC_UBYTE, bbuff)
	while head != 127:
		key = head & 0x1F # Lower 5 bits
		typ = head >> 5 # Upper 3 bits
		if typ < len(metadata_lookup) and typ >= 0:
			val = unpack(metadata_lookup[typ], bbuff)
		elif typ == 6:
			val = [unpack(MC_INT, bbuff) for i in range(3)]
		else:
			return None
		metadata.append((key, (typ, val)))
		head = unpack(MC_UBYTE, bbuff)
	return metadata

def pack_metadata(metadata):
	o = b''
	for key, tmp in data:
		typ, val = tmp
		o += pack(MC_UBYTE, (typ << 5)|key)
		if typ < len(metadata_lookup) and typ >= 0:
			o += pack(metadata_lookup[typ], bbuff)
		elif typ == 6:
			for i in range(3):
				o += pack(MC_INT, val[i])
		else:
			return None
	o += pack(MC_BYTE, 127)
	return o

endian = '>'

def unpack(data_type, bbuff):
	if data_type < len(mcdata.data_structs):
		format = mcdata.data_structs[data_type]
		return struct.unpack(endian+format[0], bbuff.recv(format[1]))[0]
	elif data_type == MC_VARINT:
		return unpack_varint(bbuff)
	elif data_type == MC_STRING:
		return bbuff.recv(unpack(MC_VARINT, bbuff)).decode('utf-8')
	elif data_type == MC_SLOT:
		return unpack_slot(bbuff)
	elif data_type == MC_META:
		return unpack_metadata(bbuff)
	else:
		return None

def pack(data_type, data):
	if data_type < len(mcdata.data_structs):
		format = mcdata.data_structs[data_type]
		return struct.pack(endian+format[0], data)
	elif data_type == MC_VARINT:
		return pack_varint(data)
	elif data_type == MC_STRING:
		data = data.encode('utf-8')
		return pack(MC_VARINT, len(data)) + data
	elif data_type == MC_SLOT:
		return pack_slot(data)
	elif data_type == MC_META:
		return pack_metadata(data)
	else:
		return None