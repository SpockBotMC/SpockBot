import struct
import zlib
from spock.mcp import mcdata
from spock.mcp import datautils
from spock.mcp import nbt
from spock import utils
from spock.mcp.mcdata import (
	MC_BOOL, MC_UBYTE, MC_BYTE, MC_USHORT, MC_SHORT, MC_UINT, MC_INT,
	MC_LONG, MC_FLOAT, MC_DOUBLE, MC_VARINT, MC_VARLONG, MC_UUID, MC_POSITION,
	MC_STRING, MC_CHAT, MC_SLOT, MC_META
)

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
		length = datautils.unpack(MC_SHORT, bbuff)
		packet.data['public_key'] = bbuff.recv(length)
		length = datautils.unpack(MC_SHORT, bbuff)
		packet.data['verify_token'] = bbuff.recv(length)
		return packet

	def encode_extra(packet):
		o  = datautils.pack(MC_SHORT, len(packet.data['public_key']))
		o += packet.data['public_key']
		o += datautils.pack(MC_SHORT, len(packet.data['verify_token']))
		o += packet.data['verify_token']
		return o

#Login CLIENT_TO_SERVER 0x01 Encryption Response
@extension((mcdata.LOGIN_STATE, mcdata.CLIENT_TO_SERVER, 0x01))
class ExtensionLCTS01:
	def decode_extra(packet, bbuff):
		length = datautils.unpack(MC_SHORT, bbuff)
		packet.data['shared_secret'] = bbuff.recv(length)
		length = datautils.unpack(MC_SHORT, bbuff)
		packet.data['verify_token'] = bbuff.recv(length)
		return packet

	def encode_extra(packet):
		o  = datautils.pack(MC_SHORT, len(packet.data['shared_secret']))
		o += packet.data['shared_secret']
		o += datautils.pack(MC_SHORT, len(packet.data['verify_token']))
		o += packet.data['verify_token']
		return o

#Play  SERVER_TO_CLIENT 0x0E Spawn Object
@extension((mcdata.PLAY_STATE, mcdata.SERVER_TO_CLIENT, 0x0E))
class ExtensionPSTC0E:
	def decode_extra(packet, bbuff):
		if packet.data['obj_data']:
			packet.data['speed_x'] = datautils.unpack(MC_SHORT, bbuff)
			packet.data['speed_y'] = datautils.unpack(MC_SHORT, bbuff)
			packet.data['speed_z'] = datautils.unpack(MC_SHORT, bbuff)
		return packet

	def encode_extra(packet):
		if packet.data['obj_data']:
			o  = datautils.pack(MC_SHORT, packet.data['speed_x'])
			o += datautils.pack(MC_SHORT, packet.data['speed_y'])
			o += datautils.pack(MC_SHORT, packet.data['speed_z'])
		return o

#Play  SERVER_TO_CLIENT 0x13 Destroy Entities
@extension((mcdata.PLAY_STATE, mcdata.SERVER_TO_CLIENT, 0x13))
class ExtensionPSTC13:
	def decode_extra(packet, bbuff):
		count = datautils.unpack(MC_VARINT, bbuff)
		packet.data['eids'] = [
			datautils.unpack(MC_VARINT, bbuff) for i in range(count)
		]
		return packet

	def encode_extra(packet):
		o = datautils.pack(MC_VARINT, len(packet.data['eids']))
		for eid in packet.data['eids']:
			o += datautils.pack(MC_VARINT, eid)
		return o

#Play  SERVER_TO_CLIENT 0x20 Entity Properties
@extension((mcdata.PLAY_STATE, mcdata.SERVER_TO_CLIENT, 0x20))
class ExtensionPSTC20:
	def decode_extra(packet, bbuff):
		packet.data['properties'] = []
		for i in range(datautils.unpack(MC_INT, bbuff)):
			prop = {
				'key': datautils.unpack(MC_STRING, bbuff),
				'value': datautils.unpack(MC_DOUBLE, bbuff),
				'modifiers': [],
			}
			for j in range(datautils.unpack(MC_VARINT, bbuff)):
				prop['modifiers'].append({
					'uuid': datautils.unpack(MC_UUID, bbuff),
					'amount': datautils.unpack(MC_DOUBLE, bbuff),
					'operation': datautils.unpack(MC_BYTE, bbuff),
				})
			packet.data['properties'].append(prop)
		return packet

	def encode_extra(packet):
		o = datautils.pack(MC_INT, len(packet.data['properties']))
		for prop in packet.data['properties']:
			o += datautils.pack(MC_STRING, prop['key'])
			o += datautils.pack(MC_DOUBLE, prop['value'])
			o += datautils.pack(MC_SHORT, len(prop['modifiers']))
			for modifier in prop['modifiers']:
				o += datautils.pack(MC_UUID, modifier['uuid'])
				o += datautils.pack(MC_DOUBLE, modifier['amount'])
				o += datautils.pack(MC_BYTE, modifier['operation'])
		return o

#Play  SERVER_TO_CLIENT 0x21 Chunk Data
@extension((mcdata.PLAY_STATE, mcdata.SERVER_TO_CLIENT, 0x21))
class ExtensionPSTC21:
	def decode_extra(packet, bbuff):
		packet.data['data'] = bbuff.recv(datautils.unpack(MC_VARINT, bbuff))
		return packet

	def encode_extra(packet):
		o = datautils.pack(MC_VARINT, len(data))
		o += packet.data['data']
		return o

#Play  SERVER_TO_CLIENT 0x22 Multi Block Change
@extension((mcdata.PLAY_STATE, mcdata.SERVER_TO_CLIENT, 0x22))
class ExtensionPSTC22:
	def decode_extra(packet, bbuff):
		packet.data['blocks'] = []
		for i in range(datautils.unpack(MC_VARINT, bbuff)):
			data = datautils.unpack(MC_USHORT, bbuff)
			packet.data['blocks'].append({
				'y': data&0xFF,
				'z': (data>>8)&0xF,
				'x': (data>>12)&0xF,
				'block_id': datautils.unpack(MC_VARINT, bbuff),
			})
		return packet

	def encode_extra(packet):
		o  = datautils.pack(MC_VARINT, len(packet.data['blocks']))
		for block in packet.data['blocks']:
			o += datautils.pack(MC_USHORT,
				(block['y']&0xFF) +
				((block['z']&0xF)<<8) +
				((block['x']&0xF)<<12)
			)
			o += datautils.pack(MC_VARINT, block['block_id'])
		return o

#Play  SERVER_TO_CLIENT 0x26 Map Chunk Bulk
@extension((mcdata.PLAY_STATE, mcdata.SERVER_TO_CLIENT, 0x26))
class ExtensionPSTC26:
	def decode_extra(packet, bbuff):
		sky_light = datautils.unpack(MC_BOOL, bbuff)
		count = datautils.unpack(MC_VARINT, bbuff)
		packet.data['sky_light'] = sky_light
		packet.data['metadata'] = [{
			'chunk_x': datautils.unpack(MC_INT, bbuff),
			'chunk_z': datautils.unpack(MC_INT, bbuff),
			'primary_bitmap': datautils.unpack(MC_USHORT, bbuff),
		} for i in range(count)]
		packet.data['data'] = bbuff.flush()
		return packet

	def encode_extra(packet):
		o = datautils.pack(MC_BOOL, packet.data['sky_light'])
		o += datautils.pack(MC_VARINT, packet.data['metadata'])
		for metadata in packet.data['metadata']:
			o += datautils.pack(MC_INT, metadata['chunk_x'])
			o += datautils.pack(MC_INT, metadata['chunk_z'])
			o += datautils.pack(MC_USHORT, metadata['primary_bitmap'])
		o += packet.data['data']
		return o

#Play  SERVER_TO_CLIENT 0x27 Explosion
@extension((mcdata.PLAY_STATE, mcdata.SERVER_TO_CLIENT, 0x27))
class ExtensionPSTC27:
	def decode_extra(packet, bbuff):
		packet.data['blocks'] = [
			[datautils.unpack(MC_BYTE, bbuff) for j in range(3)]
		for i in range(datautils.unpack(MC_INT, bbuff))]
		packet.data['player_x'] = datautils.unpack(MC_FLOAT, bbuff)
		packet.data['player_y'] = datautils.unpack(MC_FLOAT, bbuff)
		packet.data['player_z'] = datautils.unpack(MC_FLOAT, bbuff)
		return packet

	def encode_extra(packet):
		o = datautils.pack(MC_INT, len(packet.data['blocks']))
		for block in packet.data['blocks']:
			for coord in block:
				o += datautils.pack(MC_BYTE, coord)
		o += datautils.pack(MC_FLOAT, packet.data['player_x'])
		o += datautils.pack(MC_FLOAT, packet.data['player_y'])
		o += datautils.pack(MC_FLOAT, packet.data['player_z'])
		return o

#Play  SERVER_TO_CLIENT 0x2A Particle
@extension((mcdata.PLAY_STATE, mcdata.SERVER_TO_CLIENT, 0x2A))
class ExtensionPSTC2A:
	def decode_extra(packet, bbuff):
		packet.data['data'] = [
			datautils.unpack(MC_VARINT, bbuff)
		for i in range(datautils.particles[packet.data['id']])]
		return packet

	def encode_extra(packet):
		o = b''
		for i in range(datautils.particles[packet.data['id']]):
			o += datautils.pack(MC_VARINT, packet.data['data'][i])
		return o

#Play  SERVER_TO_CLIENT 0x2D Open Window
@extension((mcdata.PLAY_STATE, mcdata.SERVER_TO_CLIENT, 0x2D))
class ExtensionPSTC2D:
	def decode_extra(packet, bbuff):
		if packet.data['inv_type'] == 'EntityHorse':
			packet.data['eid'] = datautils.unpack(MC_INT, bbuff)
		return packet

	def encode_extra(packet):
		if packet.data['inv_type'] == 'EntityHorse':
			return datautils.pack(MC_INT, packet.data['eid'])


#Play  SERVER_TO_CLIENT 0x30 Window Items
@extension((mcdata.PLAY_STATE, mcdata.SERVER_TO_CLIENT, 0x30))
class ExtensionPSTC30:
	def decode_extra(packet, bbuff):
		packet.data['slots'] = [
			datautils.unpack(MC_SLOT, bbuff)
		for i in range(datautils.unpack(MC_SHORT, bbuff))]
		return packet

	def encode_extra(packet):
		o = datautils.pack(MC_SHORT, len(packet.data['slots']))
		for slot in packet.data['slots']:
			o += datautils.pack(MC_SLOT, slot)
		return o

#TODO: Actually decode the map data into a useful format
#Play  SERVER_TO_CLIENT 0x34 Maps
@extension((mcdata.PLAY_STATE, mcdata.SERVER_TO_CLIENT, 0x34))
class ExtensionPSTC34:
	def decode_extra(packet, bbuff):
		packet.data['icons'] = []
		for i in range(datautils.unpack(MC_VARINT, bbuff)):
			byte = datautils.unpack(MC_UBYTE, bbuff)
			packet.icons.append(
				'direction': byte>>8,
				'type': byte&0x0F,
				'x': datautils.unpack(MC_BYTE, bbuff),
				'y': datautils.unpack(MC_BYTE, bbuff),
			)
		packet.data['columns'] = datautils.unpack(MC_BYTE, bbuff)
		if packet.data['columns']:
			packet.data['rows'] = datautils.unpack(MC_BYTE, bbuff)
			packet.data['x'] = datautils.unpack(MC_BYTE, bbuff)
			packet.data['y'] = datautils.unpack(MC_BYTE, bbuff)
			packet.data['data'] = bbuff.recv(datautils.unpack(MC_VARINT, bbuff))
		return packet

	def encode_extra(packet):
		o = datautils.pack(MC_VARINT, len(packet.data['icons']))
		for icon in packet.data['icons']:
			byte = (packet.data['direction']<<8)|(packet.data['type']&0x0F)
			o += datautils.pack(MC_UBYTE, byte)
			o += datautils.pack(MC_BYTE, packet.data['x'])
			o += datautils.pack(MC_BYTE, packet.data['y'])
		o += datautils.pack(MC_BYTE, packet.data['columns'])
		if packet.data['columns']:
			o += datautils.pack(MC_BYTE, packet.data['rows'])
			o += datautils.pack(MC_BYTE, packet.data['x'])
			o += datautils.pack(MC_BYTE, packet.data['y'])
			o += datautils.pack(MC_VARINT, len(packet.data['data']))
			o += packet.data['data']
		return o

#Play  SERVER_TO_CLIENT 0x35 Update Block Entity
@extension((mcdata.PLAY_STATE, mcdata.SERVER_TO_CLIENT, 0x35))
class ExtensionPSTC35:
	def decode_extra(packet, bbuff):
		data = bbuff.flush()
		assert(datautils.unpack(MC_BYTE, data) == nbt.TAG_COMPOUND)
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
		return bbuff.flush()

#Play  SERVER_TO_CLIENT 0x37 Statistics
@extension((mcdata.PLAY_STATE, mcdata.SERVER_TO_CLIENT, 0x37))
class ExtensionPSTC37:
	def decode_extra(packet, bbuff):
		packet.data['entries'] = [[
			datautils.unpack(MC_STRING, bbuff),
			datautils.unpack(MC_VARINT, bbuff)
		] for i in range(datautils.unpack(MC_VARINT, bbuff))]
		return packet

	def encode_extra(packet):
		o = datautils.pack(MC_VARINT, len(packet.data['entries']))
		for entry in packet.data['entries']:
			o += datautils.pack(MC_STRING, entry[0])
			o += datautils.pack(MC_VARINT, entry[1])
		return o

#Play  SERVER_TO_CLIENT 0x38 Player List Item
@extension((mcdata.PLAY_STATE, mcdata.SERVER_TO_CLIENT, 0x38))
class ExtensionPSTC38:
	def decode_extra(packet, bbuff):
		action = packet.data['action']
		packet.data['player_list'] = []
		for i in range(datautils.unpack(MC_VARINT, bbuff)):
			item = {'uuid': datautils.unpack(MC_UUID, bbuff)}
			if action == mcdata.PL_ADD_PLAYER:
				item['name'] = datautils.unpack(MC_STRING, bbuff)
				item['properties'] = []
				for i in range(datautils.unpack(MC_VARINT, bbuff)):
					prop = {
						'name': datautils.unpack(MC_STRING, bbuff),
						'value': datautils.unpack(MC_STRING, bbuff),
						'signed': datautils.unpack(MC_BOOL, bbuff),
					}
					if prop['signed']:
						prop['signature'] = datautils.unpack(MC_STRING, bbuff)
					item['properties'].append(prop)
			if action == mcdata.PL_ADD_PLAYER or action == mcdata.PL_UPDATE_GAMEMODE:
				item['gamemode'] = datautils.unpack(MC_VARINT, bbuff)
			if action == mcdata.PL_ADD_PLAYER or action == mcdata.PL_UPDATE_LATENCY:
				item['ping'] = datautils.unpack(MC_VARINT, bbuff)
			if action == mcdata.PL_ADD_PLAYER or action == mcdata.PL_UPDATE_DISPLAY:
				item['has_display'] = datautils.unpack(MC_BOOL, bbuff)
				if item['has_display']:
					item['display_name'] = datautils.unpack(MC_CHAT, bbuff)
			packet.data['player_list'].append(item)


	def encode_extra(packet):
		action = packet.data['action']
		o = datautils.pack(MC_VARINT, len(packet.data['player_list']))
		for item in packet.data['player_list']:
			o += datautils.pack(MC_UUID, item['uuid'])
			if action == mcdata.PL_ADD_PLAYER:
				o += datautils.pack(MC_STRING, item['name'])
				o += datautils.pack(MC_VARINT, len(item['properties']))
				for prop in item['properties']:
					o += datautils.pack(MC_STRING, prop['name'])
					o += datautils.pack(MC_STRING, prop['value'])
					o += datautils.pack(MC_BOOL, prop['signed'])
					if prop['signed']:
						o += datautils.pack(MC_STRING, prop['signature'])
			if action == mcdata.PL_ADD_PLAYER or action == mcdata.PL_UPDATE_GAMEMODE:
				o += datautils.pack(MC_VARINT, item['gamemode'])
			if action == mcdata.PL_ADD_PLAYER or action == mcdata.PL_UPDATE_LATENCY:
				o += datautils.pack(MC_VARINT, item['ping'])
			if action == mcdata.PL_ADD_PLAYER or action == mcdata.PL_UPDATE_DISPLAY:
				o += datautils.pack(MC_BOOL, item['has_display'])
				if item['has_display']:
					o += datautils.pack(MC_CHAT, item['display_name'])
		return o

#Play  SERVER_TO_CLIENT 0x3A Tab-Complete
@extension((mcdata.PLAY_STATE, mcdata.SERVER_TO_CLIENT, 0x3A))
class ExtensionPSTC3A:
	def decode_extra(packet, bbuff):
		packet.data['matches'] = [
			datautils.unpack(MC_STRING, bbuff)
		for i in range(datautils.unpack(MC_VARINT, bbuff))]
		return packet

	def encode_extra(packet):
		o = datautils.pack(MC_VARINT, len(packet.data['matches']))
		for match in packet.data['matches']:
			o += datautils.pack(MC_STRING, match)
		return o

#Play  SERVER_TO_CLIENT 0x3B Scoreboard Objective
@extension((mcdata.PLAY_STATE, mcdata.SERVER_TO_CLIENT, 0x3B))
class ExtensionPSTC3B:
	def decode_extra(packet, bbuff):
		if packet.data['action'] == 0 or packet.data['action'] == 2:
			packet.data['obj_val'] = datautils.unpack(MC_STRING, bbuff)
			packet.data['type'] = datautils.unpack(MC_STRING, bbuff)
		return packet

	def encode_extra(packet):
		o = b''
		if packet.data['action'] == 0 or packet.data['action'] == 2:
			o += datautils.pack(MC_STRING, packet.data['obj_val'])
			o += datautils.pack(MC_STRING, packet.data['type'])
		return o

#Play  SERVER_TO_CLIENT 0x3C Update Score
@extension((mcdata.PLAY_STATE, mcdata.SERVER_TO_CLIENT, 0x3C))
class ExtensionPSTC3C:
	def decode_extra(packet, bbuff):
		if packet.data['action'] == 0:
			packet.data['value'] = datautils.unpack(MC_VARINT, bbuff)
		return packet

	def encode_extra(packet):
		o = b''
		if packet.data['action'] == 0:
			o += datautils.pack(MC_VARINT, packet.data['value'])
		return o

#Play  SERVER_TO_CLIENT 0x3E Teams
@extension((mcdata.PLAY_STATE, mcdata.SERVER_TO_CLIENT, 0x3E))
class ExtensionPSTC3E:
	def decode_extra(packet, bbuff):
		action = packet.data['action']
		if action == 0 or action == 2:
			packet.data['display_name'] = datautils.unpack(MC_STRING, bbuff)
			packet.data['team_prefix'] = datautils.unpack(MC_STRING, bbuff)
			packet.data['team_suffix'] = datautils.unpack(MC_STRING, bbuff)
			packet.data['friendly_fire'] = datautils.unpack(MC_BYTE, bbuff)
			packet.data['name_visibility'] = datautils.unpack(MC_STRING, bbuff)
		if action == 0 or action == 3 or action == 4:
			packet.data['players'] = [
				datautils.unpack(MC_STRING, bbuff)
			for i in range(datautils.unpack(MC_VARINT, bbuff))]
		return packet

	def encode_extra(packet):
		action = packet.data['action']
		o = b''
		if action == 0 or action == 2:
			o += datautils.pack(MC_STRING, packet.data['display_name'])
			o += datautils.pack(MC_STRING, packet.data['team_prefix'])
			o += datautils.pack(MC_STRING, packet.data['team_suffix'])
			o += datautils.pack(MC_BYTE, packet.data['friendly_fire'])
			o += datautils.pack(MC_STRING, packet.data['name_visibility'])
		if action == 0 or action == 3 or action == 4:
			o += datautils.pack(MC_VARINT, len(packet.data['players']))
			for player in packet.data['players']:
				o += datautils.pack(MC_STRING, player)
		return o

#Play  SERVER_TO_CLIENT 0x3F Plugin Message
#Play  CLIENT_TO_SERVER 0x17 Plugin Message
@extension((mcdata.PLAY_STATE, mcdata.SERVER_TO_CLIENT, 0x3F))
@extension((mcdata.PLAY_STATE, mcdata.CLIENT_TO_SERVER, 0x17))
class ExtensionPluginMessage:
	def decode_extra(packet, bbuff):
		packet.data['data'] = bbuff.flush()
		return packet

	def encode_extra(packet):
		o += packet.data['data']
		return o
