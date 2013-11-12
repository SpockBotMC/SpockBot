import struct
import zlib
from spock.mcp import mcdata
from spock.mcp import datautils
from spock.mcp import nbt
from spock import utils

hashed_extensions = {}
extensions = tuple(tuple({} for i in j) for j in mcdata.packet_structs)
def extension(ident):
	def inner(cl):
		hashed_extensions[ident] = cl
		extensions[ident[0]][ident[1]][ident[2]] = cl
		return cl
	return inner

#Login SERVER_TO_CLIENT 0x01 Encryption Request
@extension((mcdata.LOGIN_STATE, mcdata.SERVER_TO_CLIENT, 0x01))
class ExtensionLSTC01:
	def decode_extra(packet, bbuff):
		length = datautils.unpack('short', bbuff)
		packet.data['public_key'] = bbuff.recv(length)
		length = datautils.unpack('short', bbuff)
		packet.data['verify_token'] = bbuff.recv(length)
		return packet
	
	def encode_extra(packet):
		o  = pack('short', len(packet.data['public_key']))
		o += packet.data['public_key']
		o += pack('short', len(packet.data['verify_token']))
		o += packet.data['verify_token']
		return o

#Login CLIENT_TO_SERVER 0x01 Encryption Response
@extension((mcdata.LOGIN_STATE, mcdata.CLIENT_TO_SERVER, 0x01))
class ExtensionLCTS01:
	def decode_extra(packet, bbuff):
		length = datautils.unpack('short', bbuff)
		packet.data['shared_secret'] = bbuff.recv(length)
		length = datautils.unpack('short', bbuff)
		packet.data['verify_token'] = bbuff.recv(length)
		return packet
	
	def encode_extra(packet):
		o  = pack('short', len(packet.data['shared_secret']))
		o += packet.data['shared_secret']
		o += pack('short', len(packet.data['verify_token']))
		o += packet.data['verify_token']
		return o

#Play  SERVER_TO_CLIENT 0x0E Spawn Object
@extension((mcdata.PLAY_STATE, mcdata.SERVER_TO_CLIENT, 0x0E))
class ExtensionPSTC0E:
	def decode_extra(packet, bbuff):
		if packet.data['obj_data']:
			packet['speed_x'] = datautils.unpack('short', bbuff)
			packet['speed_y'] = datautils.unpack('short', bbuff)
			packet['speed_z'] = datautils.unpack('short', bbuff)
		return packet

	def encode_extra(packet):
		if packet.data['obj_data']:
			o  = datautils.pack('short', packet['speed_x'])
			o += datautils.pack('short', packet['speed_y'])
			o += datautils.pack('short', packet['speed_z'])
		return o

#Play  SERVER_TO_CLIENT 0x13 Destroy Entities
@extension((mcdata.PLAY_STATE, mcdata.SERVER_TO_CLIENT, 0x13))
class ExtensionPSTC13:
	def decode_extra(packet, bbuff):
		count = datautils.unpack('byte', bbuff)
		packet['eids'] = [
			datautils.unpack('int', bbuff) for i in range(count)
		]
		return packet

	def encode_extra(packet):
		o = datautils.pack('int', len(packet.data['eids']))
		for eid in packet.data['eids']:
			o += datautils.pack('int', eid)
		return o

#Play  SERVER_TO_CLIENT 0x20 Entity Properties
@extension((mcdata.PLAY_STATE, mcdata.SERVER_TO_CLIENT, 0x20))
class ExtensionPSTC20:
	def decode_extra(packet, bbuff):
		packet.data['properties'] = []
		for i in range(datautils.unpack('int', bbuff)):
			prop = {
				'key': datautils.unpack('string', bbuff),
				'value': datautils.unpack('double', bbuff),
				'modifiers': []
			}
			for j in range(datautils.unpack('short', bbuff)):
				a, b = struct.unpack('>QQ', bbuff.recv(16))
				prop['modifiers'].append({
					'uuid': (a<<64)|b,
					'amount': datautils.unpack('double', bbuff),
					'operation': datautils.unpack('byte', bbuff),
				})
			packet.data['properties'].append(prop)
		return packet

	def encode_extra(packet):
		o = datautils.pack('int', len(packet.data['properties']))
		for prop in packet.data['properties']:
			o += datautils.pack('string', prop['key'])
			o += datautils.pack('double', prop['value'])
			o += datautils.pack('short', len(prop['modifiers']))
			for modifier in prop['modifiers']:
				o += struct.pack('>QQ',
					(modifier['uuid']>>64)&((1<<64)-1),
					modifier['uuid']&((1<<64)-1)
				)
				o += datautils.pack('double', modifier['amount'])
				o += datautils.pack('byte', modifier['operation'])
		return o

#Play  SERVER_TO_CLIENT 0x21 Chunk Data
@extension((mcdata.PLAY_STATE, mcdata.SERVER_TO_CLIENT, 0x21))
class ExtensionPSTC21:
	def decode_extra(packet, bbuff):
		packet.data['byte_array'] = zlib.decompress(
			bbuff.recv(datautils.unpack('int', bbuff))
		)
		return packet

	def encode_extra(packet):
		data = zlib.compress(packet.data['byte_array'])
		o = datautils.pack('int', len(data))
		o += data
		return o

#Play  SERVER_TO_CLIENT 0x22 Multi Block Change
@extension((mcdata.PLAY_STATE, mcdata.SERVER_TO_CLIENT, 0x22))
class ExtensionPSTC22:
	def decode_extra(packet, bbuff):
		count = datautils.unpack('short', bbuff)
		assert(count == 4*datautils.unpack('int', bbuff))
		packet.data['blocks'] = []
		for i in range(count):
			data = unpack('uint', bbuff)
			packet.data['blocks'].append({
				'metadata': (data	 )&0xF,
				'type':	    (data>> 4)&0xFFF,
				'y':		(data>>16)&0xFF,
				'z':		(data>>24)&0xF,
				'x':		(data>>28)&0xF,
			})
		return packet

	def encode_extra(packet):
		o  = datautils.pack('short', len(packet.data['blocks']))
		o += datautils.pack('int', 4*len(packet.data['blocks']))
		for block in packet.data['blocks']:
			o += datautils.pack('uint',
				block['metadata']  +
				(block['type']<<4) +
				(block['y'] << 16) +
				(block['z'] << 24) +
				(block['x'] << 28)
			)
		return o

#Play  SERVER_TO_CLIENT 0x26 Map Chunk Bulk
@extension((mcdata.PLAY_STATE, mcdata.SERVER_TO_CLIENT, 0x26))
class ExtensionPSTC26:
	def decode_extra(packet, bbuff):
		count = datautils.unpack('short', bbuff)
		size = datautils.unpack('int', bbuff)
		packet.data['sky_light'] = datautils.unpack('bool', bbuff)
		packet.data['data'] = zlib.decompress(bbuff.recv(size))
		packet.data['metadata'] = [{
			'chunk_x': datautils.unpack('int', bbuff)
			'chunk_y': datautils.unpack('int', bbuff)
			'primary_bitmap': datautils.unpack('ushort', bbuff)
			'add_bitmap': datautils.unpack('ushort', bbuff)
		} for i in range(count)]
		return packet

	def encode_extra(packet):
		data = zlib.compress(packet.data['data'])
		o = datautils.pack('short', len(packet.data['metadata']))
		o += datautils.pack('int', len(data))
		o += datautils.pack('bool', packet.data['sky_light'])
		for metadata in packet.data['metadata']:
			o += datautils.pack('int', metadata['chunk_x'])
			o += datautils.pack('int', metadata['chunk_y'])
			o += datautils.pack('ushort', metadata['primary_bitmap'])
			o += datautils.pack('ushort', metadata['add_bitmap'])
		return o

#Play  SERVER_TO_CLIENT 0x27 Explosion
@extension((mcdata.PLAY_STATE, mcdata.SERVER_TO_CLIENT, 0x27))
class ExtensionPSTC27:
	def decode_extra(packet, bbuff):
		packet.data['blocks'] = [
			[datautils.unpack('byte', bbuff) for j in range(3)]
		for i in range(datautils.unpack('int', bbuff))]
		packet.data['player_x'] = datautils.unpack('float', bbuff)
		packet.data['player_y'] = datautils.unpack('float', bbuff)
		packet.data['player_z'] = datautils.unpack('float', bbuff)
		return packet

	def encode_extra(packet):
		o = datautils.pack('int', len(packet.data['blocks']))
		for block in packet.data['blocks']:
			for coord in block:
				o += datautils.pack('byte', coord)
		o += datautils.pack('float', packet.data['player_x'])
		o += datautils.pack('float', packet.data['player_y'])
		o += datautils.pack('float', packet.data['player_z'])
		return o

#Play  SERVER_TO_CLIENT 0x30 Window Items
@extension((mcdata.PLAY_STATE, mcdata.SERVER_TO_CLIENT, 0x30))
class ExtensionPSTC30:
	def decode_extra(packet, bbuff):
		packet.data['slots'] = [
			datautils.unpack('slot', bbuff)
		for i in range(datautils.unpack('short', bbuff))]
		return packet

	def encode_extra(packet):
		o = datautils.pack('short', len(packet.data['slots']))
		for slot in packet.data['slots']:
			o += datautils.pack('slot', slot)
		return o

#TODO: Actually decode the map data into a useful format
#Play  SERVER_TO_CLIENT 0x34 Maps
@extension((mcdata.PLAY_STATE, mcdata.SERVER_TO_CLIENT, 0x34))
class ExtensionPSTC34:
	def decode_extra(packet, bbuff):
		packet.data['byte_array'] = bbuff.recv(datautils.unpack('short', bbuff))
		return packet

	def encode_extra(packet):
		o = datautils.pack(len('byte_array'))
		o += packet.data['byte_array']
		return o

#Play  SERVER_TO_CLIENT 0x35 Update Block Entity
@extension((mcdata.PLAY_STATE, mcdata.SERVER_TO_CLIENT, 0x35))
class ExtensionPSTC35:
	def decode_extra(packet, bbuff):
		data = bbuff.recv(datautils.unpack('short', bbuff))
		data = utils.BoundBuffer(zlib.decompress(data, 16+zlib.MAX_WBITS))
		assert(unpack('byte', data) == nbt.TAG_COMPOUND)
		name = nbt.TAG_String(buffer = data)
		nbt_data = nbt.TAG_Compound(buffer = data)
		nbt_data.name = name
		packet.data['nbt'] = nbt_data
		return packet

	def encode_extra(packet):
		bbuff = utils.BoundBuffer()
		TAG_Byte(packet.data['nbt'].id)._render_buffer(bbuff)
		TAG_String(packet.data['nbt'].name)._render_buffer(bbuff)
		packet.data['nbt']._render_buffer(bbuff)
		compress = zlib.compressobj(wbits = 16+zlib.MAX_WBITS)
		data = compress.compress(bbuff.flush())
		data += compress.flush()
		o = datautils.pack('short', len(data))
		o += data
		return o

#Play  SERVER_TO_CLIENT 0x37 Statistics
@extension((mcdata.PLAY_STATE, mcdata.SERVER_TO_CLIENT, 0x37))
class ExtensionPSTC37:
	def decode_extra(packet, bbuff):
		packet.data['entries'] = [[
			datautils.unpack('string', bbuff), 
			datautils.unpack('varint', bbuff)
		] for i in range(datautils.unpack('varint', bbuff))]
		return packet

	def encode_extra(packet):
		o = datautils.pack('varint', len(packet.data['entries']))
		for entry in packet.data['entries']:
			o += datautils.pack('string', entry[0])
			o += datautils.pack('varint', entry[1])
		return o

#Play  SERVER_TO_CLIENT 0x3A Tab-Complete
@extension((mcdata.PLAY_STATE, mcdata.SERVER_TO_CLIENT, 0x3A))
class ExtensionPSTC3A:
	def decode_extra(packet, bbuff):
		packet.data['matches'] = [
			datautils.unpack('string', bbuff)
		for i in range(datautils.unpack('varint', bbuff))]
		return packet

	def encode_extra(packet):
		o = datautils.pack('varint', len(packet.data['matches']))
		for match in packet.data['matches']:
			o += datautils.pack('string', match)
		return o

#Play  SERVER_TO_CLIENT 0x3E Teams
@extension((mcdata.PLAY_STATE, mcdata.SERVER_TO_CLIENT, 0x3E))
class ExtensionPSTC3E:
	def decode_extra(packet, bbuff):
		mode = packet.data['mode']
		if mode == 0 or mode == 2:
			packet.data['display_name'] = datautils.unpack('string', bbuff)
			packet.data['team_prefix'] = datautils.unpack('string', bbuff)
			packet.data['team_suffix'] = datautils.unpack('string', bbuff)
			packet.data['friendly_fire'] = datautils.unpack('byte', bbuff)
		if mode == 0 or mode == 3 or mode == 4:
			packet.data['players'] = [
				datautils.unpack('string', bbuff)
			for i in range(datautils.unpack('short', bbuff))]
		return packet

	def encode_extra(packet):
		mode = packet.data['mode']
		o = b''
		if mode == 0 or mode == 2:
			o += datautils.pack('string', packet.data['display_name'])
			o += datautils.pack('string', packet.data['team_prefix'])
			o += datautils.pack('string', packet.data['team_suffix'])
			o += datautils.pack('byte', packet.data['friendly_fire'])
		if mode == 0 or mode == 3 or mode == 4:
			o += datautils.pack('short', len(packet.data['players']))
			for player in packet.data['players']:
				o += datautils.pack('string', player)
		return o

#Play  SERVER_TO_CLIENT 0x3F Plugin Message
#Play  CLIENT_TO_SERVER 0x17 Plugin Message
@extension((mcdata.PLAY_STATE, mcdata.SERVER_TO_CLIENT, 0x3F))
@extension((mcdata.PLAY_STATE, mcdata.CLIENT_TO_SERVER, 0x17))
class ExtensionPluginMessage:
	def decode_extra(packet, bbuff):
		packet.data['data'] = bbuff.recv(datautils.unpack('short', bbuff))
		return packet

	def encode_extra(packet):
		o = datautils.pack('short', len(packet.data['data']))
		o += data
		return o
