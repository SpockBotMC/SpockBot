import struct
import zlib
import json
from spock import utils
from spock.mcp import mcdata, nbt
from spock.mcp.mcdata import (
    MC_BOOL, MC_UBYTE, MC_BYTE, MC_USHORT, MC_SHORT, MC_UINT, MC_INT, MC_ULONG,
    MC_LONG, MC_FLOAT, MC_DOUBLE, MC_VARINT, MC_VARLONG, MC_FP_INT, MC_FP_BYTE,
    MC_UUID, MC_POSITION, MC_STRING, MC_CHAT, MC_SLOT, MC_META
)

#Unpack/Pack functions return None on error

# Minecraft varints are 32-bit signed values
# packed into Google Protobuf varints
def unpack_varint(bbuff):
    total = 0
    shift = 0
    val = 0x80
    while val & 0x80:
        val = struct.unpack('B', bbuff.read(1))[0]
        total |= (val & 0x7F) << shift
        shift += 7
    if total >= (1<<32):
        return None
    if total & (1<<31):
        total -= 1<<32
    return total

def pack_varint(val):
    if val >= (1<<31) or val < -(1<<31):
        return None
    o = b''
    if val < 0:
        val += 1<<32
    while val >= 0x80:
        bits = val & 0x7F
        val >>= 7
        o += struct.pack('B', (0x80 | bits))
    bits = val&0x7F
    o += struct.pack('B', bits)
    return o

#Like a varint, but a 64-bit signed value
def unpack_varlong(bbuff):
    total = 0
    shift = 0
    val = 0x80
    while val & 0x80:
        val = struct.unpack('B', bbuff.read(1))[0]
        total |= ((val & 0x7F) << shift)
        shift += 7
    if total >= 1<<64:
        return None
    if total & (1<<64):
        total -= 1 << 64
    return total

def pack_varlong(val):
    if val >= (1<<63) or val < -(1<<63):
        return None
    o = b''
    if val < 0:
        val += 1<<64
    while val >= 0x80:
        bits = val & 0x7F
        val >>= 7
        o += struct.pack('B', (0x80 | bits))
    bits = val & 0x7F
    o += struct.pack('B', bits)
    return o

# Three values packed into one 64-bit long
# x: 26 MSBs, y: 12 bits, z: 26 LSBs
def unpack_position(bbuff):
    position = {}
    val = unpack(MC_LONG, bbuff)
    position['x'] = val >> 38
    position['y'] = (val >> 26) & 0xFFF
    z = val & 0x3FFFFFF
    if z & (1<<25):
        z -= (1<<26)
    position['z'] = z
    return position

def pack_position(position):
    val  = (int(position['x']) & 0x3FFFFFF) << 38
    val |= (int(position['y']) & 0xFFF) << 26
    val |= (int(position['z']) & 0x3FFFFFF)
    return pack(MC_ULONG, val)

#Fixed point number where the first 5 bits are dedicated to the decimal place
#Internally vanilla mc implements these as doubles, so we do the same thing
def unpack_fixed_point(mc_type, bbuff):
    val = unpack(mc_type, bbuff)
    val = float(val) / (1<<5)
    return val

def pack_fixed_point(mc_type, val):
    val = int(val * (1<<5))
    return pack(mc_type, val)

# Slots are dictionaries that hold info about
# inventory items, they also have funky
# enchantment data

def unpack_slot(bbuff):
    slot = {}
    slot['id'] = unpack(MC_SHORT, bbuff)
    if slot['id'] != -1:
        slot['amount'] = unpack(MC_BYTE, bbuff)
        slot['damage'] = unpack(MC_SHORT, bbuff)
        nbt_start = unpack(MC_BYTE, bbuff)
        if nbt_start > 0:
            if nbt_start != nbt.TAG_COMPOUND:
                return None
            name = nbt.TAG_String(buffer = bbuff).value
            ench = nbt.TAG_Compound(buffer = bbuff)
            ench.name = name
            slot['enchants'] = ench
    return slot

def pack_slot(slot):
    o = pack(MC_SHORT, slot['id'])
    if slot['id'] != -1:
        o += pack(MC_BYTE, slot['amount'])
        o += pack(MC_SHORT, slot['damage'])
        if 'enchants' in slot:
            ench = slot['enchants']
            bbuff = utils.BoundBuffer()
            nbt.TAG_Byte(ench.id)._render_buffer(bbuff)
            nbt.TAG_String(ench.name)._render_buffer(bbuff)
            ench._render_buffer(bbuff)
            o += bbuff.flush()
        else:
            o += pack(MC_BYTE, 0)
    return o

# Metadata is a dictionary list thing that
# holds metadata about entities. Currently
# implemented as a list/tuple thing, might
# switch to dicts
metadata_lookup = MC_BYTE, MC_SHORT, MC_INT, MC_FLOAT, MC_STRING, MC_SLOT

def unpack_metadata(bbuff):
    metadata = []
    head = unpack(MC_UBYTE, bbuff)
    while head != 0x7F:
        key = head & 0x1F # Lower 5 bits
        typ = head >> 5 # Upper 3 bits
        if 0 <= typ < len(metadata_lookup):
            val = unpack(metadata_lookup[typ], bbuff)
        elif typ == 6:
            val = [unpack(MC_INT, bbuff)] * 3
        elif typ == 7:
            val = [unpack(MC_FLOAT, bbuff)] * 3
        else:
            return None
        metadata.append((key, (typ, val)))
        head = unpack(MC_UBYTE, bbuff)
    return metadata

def pack_metadata(data):
    o = b''
    for key, tmp in data:
        typ, val = tmp
        o += pack(MC_UBYTE, (typ << 5)|key)
        if 0 <= typ < len(metadata_lookup):
            o += pack(metadata_lookup[typ], val)
        elif typ == 6:
            for i in range(3):
                o += pack(MC_INT, val[i])
        elif typ == 7:
            for i in range(3):
                o += pack(MC_FLOAT, val[i])
        else:
            return None
    o += pack(MC_BYTE, 0x7F)
    return o

endian = '>'

def unpack(data_type, bbuff):
    if data_type < len(mcdata.data_structs):
        format = mcdata.data_structs[data_type]
        return struct.unpack(endian+format[0], bbuff.recv(format[1]))[0]
    elif data_type == MC_VARINT:
        return unpack_varint(bbuff)
    elif data_type == MC_VARLONG:
        return unpack_varlong(bbuff)
    elif data_type == MC_FP_INT:
        return unpack_fixed_point(MC_INT, bbuff)
    elif data_type == MC_FP_BYTE:
        return unpack_fixed_point(MC_BYTE, bbuff)
    elif data_type == MC_UUID:
        a, b = struct.unpack('>QQ', bbuff.recv(16))
        return (a<<64)|b
    elif data_type == MC_POSITION:
        return unpack_position(bbuff)
    elif data_type == MC_STRING:
        return bbuff.recv(unpack(MC_VARINT, bbuff)).decode('utf-8')
    elif data_type == MC_CHAT:
        return json.loads(unpack(MC_STRING, bbuff))
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
    elif data_type == MC_VARLONG:
        return pack_varlong(data)
    elif data_type == MC_FP_INT:
        return pack_fixed_point(MC_INT, data)
    elif data_type == MC_FP_BYTE:
        return pack_fixed_point(MC_BYTE, data)
    elif data_type == MC_UUID:
        return struct.pack('>QQ', (data>>64) & ((1<<64) - 1), data & ((1<<64) - 1))
    elif data_type == MC_POSITION:
        return pack_position(data)
    elif data_type == MC_STRING:
        data = data.encode('utf-8')
        return pack(MC_VARINT, len(data)) + data
    elif data_type == MC_CHAT:
        return pack(MC_STRING, json.dumps(data))
    elif data_type == MC_SLOT:
        return pack_slot(data)
    elif data_type == MC_META:
        return pack_metadata(data)
    else:
        return None
