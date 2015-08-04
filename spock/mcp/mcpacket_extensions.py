import struct
import zlib
from spock.mcp import mcdata
from spock.mcp import datautils
from spock.mcp import nbt
from spock import utils
from spock.mcp.mcdata import (
    MC_BOOL, MC_UBYTE, MC_BYTE, MC_USHORT, MC_SHORT, MC_UINT, MC_INT, MC_ULONG,
    MC_LONG, MC_FLOAT, MC_DOUBLE, MC_VARINT, MC_VARLONG, MC_FP_INT, MC_FP_BYTE,
    MC_UUID, MC_POSITION, MC_STRING, MC_CHAT, MC_SLOT, MC_META
)

hashed_extensions = {}
extensions = tuple(tuple({} for i in j) for j in mcdata.packet_structs)
def extension(state, direction, packet_id):
    def inner(cl):
        hashed_extensions[(state, direction, packet_id)] = cl
        extensions[state][direction][packet_id] = cl
        return cl
    return inner

#Login SERVER_TO_CLIENT 0x01 Encryption Request
@extension(mcdata.LOGIN_STATE, mcdata.SERVER_TO_CLIENT, 0x01)
class ExtensionLSTC01:
    @staticmethod
    def decode_extra(packet, bbuff):
        length = datautils.unpack(MC_VARINT, bbuff)
        packet.data['public_key'] = bbuff.recv(length)
        length = datautils.unpack(MC_VARINT, bbuff)
        packet.data['verify_token'] = bbuff.recv(length)
        return packet

    @staticmethod
    def encode_extra(packet):
        o  = datautils.pack(MC_VARINT, len(packet.data['public_key']))
        o += packet.data['public_key']
        o += datautils.pack(MC_VARINT, len(packet.data['verify_token']))
        o += packet.data['verify_token']
        return o

#Login CLIENT_TO_SERVER 0x01 Encryption Response
@extension(mcdata.LOGIN_STATE, mcdata.CLIENT_TO_SERVER, 0x01)
class ExtensionLCTS01:
    @staticmethod
    def decode_extra(packet, bbuff):
        length = datautils.unpack(MC_VARINT, bbuff)
        packet.data['shared_secret'] = bbuff.recv(length)
        length = datautils.unpack(MC_VARINT, bbuff)
        packet.data['verify_token'] = bbuff.recv(length)
        return packet

    @staticmethod
    def encode_extra(packet):
        o  = datautils.pack(MC_VARINT, len(packet.data['shared_secret']))
        o += packet.data['shared_secret']
        o += datautils.pack(MC_VARINT, len(packet.data['verify_token']))
        o += packet.data['verify_token']
        return o

#Play  SERVER_TO_CLIENT 0x0E Spawn Object
@extension(mcdata.PLAY_STATE, mcdata.SERVER_TO_CLIENT, 0x0E)
class ExtensionPSTC0E:
    @staticmethod
    def decode_extra(packet, bbuff):
        if packet.data['obj_data']:
            packet.data['speed_x'] = datautils.unpack(MC_SHORT, bbuff)
            packet.data['speed_y'] = datautils.unpack(MC_SHORT, bbuff)
            packet.data['speed_z'] = datautils.unpack(MC_SHORT, bbuff)
        return packet

    @staticmethod
    def encode_extra(packet):
        if packet.data['obj_data']:
            o  = datautils.pack(MC_SHORT, packet.data['speed_x'])
            o += datautils.pack(MC_SHORT, packet.data['speed_y'])
            o += datautils.pack(MC_SHORT, packet.data['speed_z'])
        return o

#Play  SERVER_TO_CLIENT 0x13 Destroy Entities
@extension(mcdata.PLAY_STATE, mcdata.SERVER_TO_CLIENT, 0x13)
class ExtensionPSTC13:
    @staticmethod
    def decode_extra(packet, bbuff):
        count = datautils.unpack(MC_VARINT, bbuff)
        packet.data['eids'] = [
            datautils.unpack(MC_VARINT, bbuff) for i in range(count)
        ]
        return packet

    @staticmethod
    def encode_extra(packet):
        o = datautils.pack(MC_VARINT, len(packet.data['eids']))
        for eid in packet.data['eids']:
            o += datautils.pack(MC_VARINT, eid)
        return o

#Play  SERVER_TO_CLIENT 0x20 Entity Properties
@extension(mcdata.PLAY_STATE, mcdata.SERVER_TO_CLIENT, 0x20)
class ExtensionPSTC20:
    @staticmethod
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

    @staticmethod
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
@extension(mcdata.PLAY_STATE, mcdata.SERVER_TO_CLIENT, 0x21)
class ExtensionPSTC21:
    @staticmethod
    def decode_extra(packet, bbuff):
        packet.data['data'] = bbuff.recv(datautils.unpack(MC_VARINT, bbuff))
        return packet

    @staticmethod
    def encode_extra(packet):
        o = datautils.pack(MC_VARINT, len(data))
        o += packet.data['data']
        return o

#Play  SERVER_TO_CLIENT 0x22 Multi Block Change
@extension(mcdata.PLAY_STATE, mcdata.SERVER_TO_CLIENT, 0x22)
class ExtensionPSTC22:
    @staticmethod
    def decode_extra(packet, bbuff):
        packet.data['blocks'] = []
        for i in range(datautils.unpack(MC_VARINT, bbuff)):
            data = datautils.unpack(MC_USHORT, bbuff)
            packet.data['blocks'].append({
                'y': data&0xFF,
                'z': (data>>8)&0xF,
                'x': (data>>12)&0xF,
                'block_data': datautils.unpack(MC_VARINT, bbuff),
            })
        return packet

    @staticmethod
    def encode_extra(packet):
        o  = datautils.pack(MC_VARINT, len(packet.data['blocks']))
        for block in packet.data['blocks']:
            o += datautils.pack(MC_USHORT,
                (block['y']&0xFF) +
                ((block['z']&0xF)<<8) +
                ((block['x']&0xF)<<12)
            )
            o += datautils.pack(MC_VARINT, block['block_data'])
        return o

#Play  SERVER_TO_CLIENT 0x26 Map Chunk Bulk
@extension(mcdata.PLAY_STATE, mcdata.SERVER_TO_CLIENT, 0x26)
class ExtensionPSTC26:
    @staticmethod
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

    @staticmethod
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
@extension(mcdata.PLAY_STATE, mcdata.SERVER_TO_CLIENT, 0x27)
class ExtensionPSTC27:
    @staticmethod
    def decode_extra(packet, bbuff):
        packet.data['blocks'] = [
            [datautils.unpack(MC_BYTE, bbuff) for j in range(3)]
        for i in range(datautils.unpack(MC_INT, bbuff))]
        packet.data['player_x'] = datautils.unpack(MC_FLOAT, bbuff)
        packet.data['player_y'] = datautils.unpack(MC_FLOAT, bbuff)
        packet.data['player_z'] = datautils.unpack(MC_FLOAT, bbuff)
        return packet

    @staticmethod
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
@extension(mcdata.PLAY_STATE, mcdata.SERVER_TO_CLIENT, 0x2A)
class ExtensionPSTC2A:
    @staticmethod
    def decode_extra(packet, bbuff):
        packet.data['data'] = [
            datautils.unpack(MC_VARINT, bbuff)
        for i in range(mcdata.particles[packet.data['id']][1])]
        return packet

    @staticmethod
    def encode_extra(packet):
        o = b''
        for i in range(mcdata.particles[packet.data['id']][1]):
            o += datautils.pack(MC_VARINT, packet.data['data'][i])
        return o

#Play  SERVER_TO_CLIENT 0x2D Open Window
@extension(mcdata.PLAY_STATE, mcdata.SERVER_TO_CLIENT, 0x2D)
class ExtensionPSTC2D:
    @staticmethod
    def decode_extra(packet, bbuff):
        if packet.data['inv_type'] == 'EntityHorse':
            packet.data['eid'] = datautils.unpack(MC_INT, bbuff)
        return packet

    @staticmethod
    def encode_extra(packet):
        if packet.data['inv_type'] == 'EntityHorse':
            return datautils.pack(MC_INT, packet.data['eid'])


#Play  SERVER_TO_CLIENT 0x30 Window Items
@extension(mcdata.PLAY_STATE, mcdata.SERVER_TO_CLIENT, 0x30)
class ExtensionPSTC30:
    @staticmethod
    def decode_extra(packet, bbuff):
        packet.data['slots'] = [
            datautils.unpack(MC_SLOT, bbuff)
        for i in range(datautils.unpack(MC_SHORT, bbuff))]
        return packet

    @staticmethod
    def encode_extra(packet):
        o = datautils.pack(MC_SHORT, len(packet.data['slots']))
        for slot in packet.data['slots']:
            o += datautils.pack(MC_SLOT, slot)
        return o

#TODO: Actually decode the map data into a useful format
#Play  SERVER_TO_CLIENT 0x34 Maps
@extension(mcdata.PLAY_STATE, mcdata.SERVER_TO_CLIENT, 0x34)
class ExtensionPSTC34:
    @staticmethod
    def decode_extra(packet, bbuff):
        packet.data['icons'] = []
        for i in range(datautils.unpack(MC_VARINT, bbuff)):
            byte = datautils.unpack(MC_UBYTE, bbuff)
            packet.data['icons'].append({
                'direction': byte>>8,
                'type': byte&0x0F,
                'x': datautils.unpack(MC_BYTE, bbuff),
                'y': datautils.unpack(MC_BYTE, bbuff),
            })
        packet.data['columns'] = datautils.unpack(MC_BYTE, bbuff)
        if packet.data['columns']:
            packet.data['rows'] = datautils.unpack(MC_BYTE, bbuff)
            packet.data['x'] = datautils.unpack(MC_BYTE, bbuff)
            packet.data['y'] = datautils.unpack(MC_BYTE, bbuff)
            packet.data['data'] = bbuff.recv(datautils.unpack(MC_VARINT, bbuff))
        return packet

    @staticmethod
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
#Play  SERVER_TO_CLIENT 0x49 Update Entity NBT
@extension(mcdata.PLAY_STATE, mcdata.SERVER_TO_CLIENT, 0x35)
@extension(mcdata.PLAY_STATE, mcdata.SERVER_TO_CLIENT, 0x49)
class ExtensionUpdateNBT:
    @staticmethod
    def decode_extra(packet, bbuff):
        tag_type = datautils.unpack(MC_BYTE, bbuff)
        if tag_type == nbt.TAG_COMPOUND:
            name = nbt.TAG_String(buffer = bbuff).value
            nbt_data = nbt.TAG_Compound(buffer = bbuff)
            nbt_data.name = name
            packet.data['nbt'] = nbt_data
        else:
            assert(tag_type == nbt.TAG_END)
            packet.data['nbt'] = None
        return packet

    @staticmethod
    def encode_extra(packet):
        bbuff = utils.BoundBuffer()
        if packet.data['nbt'] == None:
            packet.data['nbt'] = nbt._TAG_End()
        TAG_Byte(packet.data['nbt'].id)._render_buffer(bbuff)
        if packet.data['nbt'].id == nbt.TAG_COMPOUND:
            TAG_String(packet.data['nbt'].name)._render_buffer(bbuff)
            packet.data['nbt']._render_buffer(bbuff)
        return bbuff.flush()

#Play  SERVER_TO_CLIENT 0x37 Statistics
@extension(mcdata.PLAY_STATE, mcdata.SERVER_TO_CLIENT, 0x37)
class ExtensionPSTC37:
    @staticmethod
    def decode_extra(packet, bbuff):
        packet.data['entries'] = [[
            datautils.unpack(MC_STRING, bbuff),
            datautils.unpack(MC_VARINT, bbuff)
        ] for i in range(datautils.unpack(MC_VARINT, bbuff))]
        return packet

    @staticmethod
    def encode_extra(packet):
        o = datautils.pack(MC_VARINT, len(packet.data['entries']))
        for entry in packet.data['entries']:
            o += datautils.pack(MC_STRING, entry[0])
            o += datautils.pack(MC_VARINT, entry[1])
        return o

#Play  SERVER_TO_CLIENT 0x38 Player List Item
@extension(mcdata.PLAY_STATE, mcdata.SERVER_TO_CLIENT, 0x38)
class ExtensionPSTC38:
    @staticmethod
    def decode_extra(packet, bbuff):
        act = packet.data['action']
        packet.data['player_list'] = []
        for i in range(datautils.unpack(MC_VARINT, bbuff)):
            item = {'uuid': datautils.unpack(MC_UUID, bbuff)}
            if act == mcdata.PL_ADD_PLAYER:
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
            if act == mcdata.PL_ADD_PLAYER or act == mcdata.PL_UPDATE_GAMEMODE:
                item['gamemode'] = datautils.unpack(MC_VARINT, bbuff)
            if act == mcdata.PL_ADD_PLAYER or act == mcdata.PL_UPDATE_LATENCY:
                item['ping'] = datautils.unpack(MC_VARINT, bbuff)
            if act == mcdata.PL_ADD_PLAYER or act == mcdata.PL_UPDATE_DISPLAY:
                item['has_display'] = datautils.unpack(MC_BOOL, bbuff)
                if item['has_display']:
                    item['display_name'] = datautils.unpack(MC_CHAT, bbuff)
            packet.data['player_list'].append(item)


    @staticmethod
    def encode_extra(packet):
        act = packet.data['action']
        o = datautils.pack(MC_VARINT, len(packet.data['player_list']))
        for item in packet.data['player_list']:
            o += datautils.pack(MC_UUID, item['uuid'])
            if act == mcdata.PL_ADD_PLAYER:
                o += datautils.pack(MC_STRING, item['name'])
                o += datautils.pack(MC_VARINT, len(item['properties']))
                for prop in item['properties']:
                    o += datautils.pack(MC_STRING, prop['name'])
                    o += datautils.pack(MC_STRING, prop['value'])
                    o += datautils.pack(MC_BOOL, prop['signed'])
                    if prop['signed']:
                        o += datautils.pack(MC_STRING, prop['signature'])
            if act == mcdata.PL_ADD_PLAYER or act == mcdata.PL_UPDATE_GAMEMODE:
                o += datautils.pack(MC_VARINT, item['gamemode'])
            if act == mcdata.PL_ADD_PLAYER or act == mcdata.PL_UPDATE_LATENCY:
                o += datautils.pack(MC_VARINT, item['ping'])
            if act == mcdata.PL_ADD_PLAYER or act == mcdata.PL_UPDATE_DISPLAY:
                o += datautils.pack(MC_BOOL, item['has_display'])
                if item['has_display']:
                    o += datautils.pack(MC_CHAT, item['display_name'])
        return o

#Play  SERVER_TO_CLIENT 0x3A Tab-Complete
@extension(mcdata.PLAY_STATE, mcdata.SERVER_TO_CLIENT, 0x3A)
class ExtensionPSTC3A:
    @staticmethod
    def decode_extra(packet, bbuff):
        packet.data['matches'] = [
            datautils.unpack(MC_STRING, bbuff)
        for i in range(datautils.unpack(MC_VARINT, bbuff))]
        return packet

    @staticmethod
    def encode_extra(packet):
        o = datautils.pack(MC_VARINT, len(packet.data['matches']))
        for match in packet.data['matches']:
            o += datautils.pack(MC_STRING, match)
        return o

#Play  SERVER_TO_CLIENT 0x3B Scoreboard Objective
@extension(mcdata.PLAY_STATE, mcdata.SERVER_TO_CLIENT, 0x3B)
class ExtensionPSTC3B:
    @staticmethod
    def decode_extra(packet, bbuff):
        act = packet.data['action']
        if act == mcdata.SO_CREATE_BOARD or act == mcdata.SO_UPDATE_BOARD:
            packet.data['obj_val'] = datautils.unpack(MC_STRING, bbuff)
            packet.data['type'] = datautils.unpack(MC_STRING, bbuff)
        return packet

    @staticmethod
    def encode_extra(packet):
        o = b''
        act = packet.data['action']
        if act == mcdata.SO_CREATE_BOARD or act == mcdata.SO_UPDATE_BOARD:
            o += datautils.pack(MC_STRING, packet.data['obj_val'])
            o += datautils.pack(MC_STRING, packet.data['type'])
        return o

#Play  SERVER_TO_CLIENT 0x3C Update Score
@extension(mcdata.PLAY_STATE, mcdata.SERVER_TO_CLIENT, 0x3C)
class ExtensionPSTC3C:
    @staticmethod
    def decode_extra(packet, bbuff):
        if packet.data['action'] == mcdata.US_UPDATE_SCORE:
            packet.data['value'] = datautils.unpack(MC_VARINT, bbuff)
        return packet

    @staticmethod
    def encode_extra(packet):
        o = b''
        if packet.data['action'] == mcdata.US_UPDATE_SCORE:
            o += datautils.pack(MC_VARINT, packet.data['value'])
        return o

#Play  SERVER_TO_CLIENT 0x3E Teams
@extension(mcdata.PLAY_STATE, mcdata.SERVER_TO_CLIENT, 0x3E)
class ExtensionPSTC3E:
    @staticmethod
    def decode_extra(packet, bbuff):
        act = packet.data['action']
        if act == mcdata.TE_CREATE_TEAM or act == mcdata.TE_UPDATE_TEAM:
            packet.data['display_name'] = datautils.unpack(MC_STRING, bbuff)
            packet.data['team_prefix'] = datautils.unpack(MC_STRING, bbuff)
            packet.data['team_suffix'] = datautils.unpack(MC_STRING, bbuff)
            packet.data['friendly_fire'] = datautils.unpack(MC_BYTE, bbuff)
            packet.data['name_visibility'] = datautils.unpack(MC_STRING, bbuff)
            packet.data['color'] = datautils.unpack(MC_BYTE, bbuff)
        if (
            act == mcdata.TE_CREATE_TEAM or
            act == mcdata.TE_ADDPLY_TEAM or
            act == mcdata.TE_REMPLY_TEAM
        ):
            packet.data['players'] = [
                datautils.unpack(MC_STRING, bbuff)
            for i in range(datautils.unpack(MC_VARINT, bbuff))]
        return packet

    @staticmethod
    def encode_extra(packet):
        act = packet.data['action']
        o = b''
        if act == mcdata.TE_CREATE_TEAM or act == TE_UPDATE_TEAM:
            o += datautils.pack(MC_STRING, packet.data['display_name'])
            o += datautils.pack(MC_STRING, packet.data['team_prefix'])
            o += datautils.pack(MC_STRING, packet.data['team_suffix'])
            o += datautils.pack(MC_BYTE, packet.data['friendly_fire'])
            o += datautils.pack(MC_STRING, packet.data['name_visibility'])
            o += datautils.pack(MC_BYTE, packet.data['color'])
        if (
            act == mcdata.TE_CREATE_TEAM or
            act == mcdata.TE_ADDPLY_TEAM or
            act == mcdata.TE_REMPLY_TEAM
        ):
            o += datautils.pack(MC_VARINT, len(packet.data['players']))
            for player in packet.data['players']:
                o += datautils.pack(MC_STRING, player)
        return o

#Play  SERVER_TO_CLIENT 0x3F Plugin Message
#Play  CLIENT_TO_SERVER 0x17 Plugin Message
@extension(mcdata.PLAY_STATE, mcdata.SERVER_TO_CLIENT, 0x3F)
@extension(mcdata.PLAY_STATE, mcdata.CLIENT_TO_SERVER, 0x17)
class ExtensionPluginMessage:
    @staticmethod
    def decode_extra(packet, bbuff):
        packet.data['data'] = bbuff.flush()
        return packet

    @staticmethod
    def encode_extra(packet):
        o += packet.data['data']
        return o

#Play  SERVER_TO_CLIENT 0x42 Combat Event
@extension(mcdata.PLAY_STATE, mcdata.SERVER_TO_CLIENT, 0x42)
class ExtensionPSTC42:
    @staticmethod
    def decode_extra(packet, bbuff):
        if packet.data['event'] == mcdata.CE_END_COMBAT:
            packet.data['duration'] = datautils.unpack(MC_VARINT, bbuff)
            packet.data['eid'] = datautils.unpack(MC_INT, bbuff)
        if packet.data['event'] == mcdata.CE_ENTITY_DEAD:
            packet.data['player_id'] = datautils.unpack(MC_VARINT, bbuff)
            packet.data['eid'] = datautils.unpack(MC_INT, bbuff)
            packet.data['message'] = datautils.unpack(MC_STRING, bbuff)
        return packet

    @staticmethod
    def encode_extra(packet):
        o = b''
        if packet.data['event'] == mcdata.CE_END_COMBAT:
            o += datautils.pack(MC_VARINT, packet.data['duration'])
            o += datautils.pack(MC_INT, packet.data['eid'])
        if packet.data['event'] == mcdata.CE_ENTITY_DEAD:
            o += datautils.pack(MC_VARINT, packet.data['player_id'])
            o += datautils.pack(MC_INT, packet.data['eid'])
            o += datautils.pack(MC_STRING, packet.data['message'])
        return o

#Play  SERVER_TO_CLIENT 0x44 World Border
@extension(mcdata.PLAY_STATE, mcdata.SERVER_TO_CLIENT, 0x44)
class ExtensionPSTC44:
    @staticmethod
    def decode_extra(packet, bbuff):
        act = packet.data['action']
        if act == mcdata.WB_SET_SIZE:
            packet.data['radius'] = datautils.unpack(MC_VARINT, bbuff)
        if act == mcdata.WB_SET_CENTER or act == mcdata.WB_INITIALIZE:
            packet.data['x'] = datautils.unpack(MC_DOUBLE, bbuff)
            packet.data['z'] = datautils.unpack(MC_DOUBLE, bbuff)
        if act == mcdata.WB_LERP_SIZE or act == mcdata.WB_INITIALIZE:
            packet.data['old_radius'] = datautils.unpack(MC_DOUBLE, bbuff)
            packet.data['new_radius'] = datautils.unpack(MC_DOUBLE, bbuff)
            packet.data['speed'] = datautils.unpack(MC_VARLONG, bbuff)
        if act == mcdata.WB_INITIALIZE:
            packet.data['port_tele_bound'] = datautils.unpack(MC_VARINT, bbuff)
        if act == mcdata.WB_SET_WARN_TIME or act == mcdata.WB_INITIALIZE:
            packet.data['warn_time'] = datautils.unpack(MC_VARINT, bbuff)
        if act == mcdata.WB_SET_WARN_BLOCKS or act == mcdata.WB_INITIALIZE:
            packet.data['warn_blocks'] = datautils.unpack(MC_VARINT, bbuff)
        return packet

    @staticmethod
    def encode_extra(packet):
        o = b''
        act = packet.data['action']
        if act == mcdata.WB_SET_SIZE:
            o += datautils.pack(MC_DOUBLE, packet.data['radius'])
        if act == mcdata.WB_SET_CENTER or act == mcdata.WB_INITIALIZE:
            o += datautils.pack(MC_DOUBLE, packet.data['x'])
            o += datautils.pack(MC_DOUBLE, packet.data['y'])
        if act == mcdata.WB_LERP_SIZE or act == mcdata.WB_INITIALIZE:
            o += datautils.pack(MC_DOUBLE, packet.data['old_radius'])
            o += datautils.pack(MC_DOUBLE, packet.data['new_radius'])
            o += datautils.pack(MC_VARLONG, packet.data['speed'])
        if act == mcdata.WB_INITIALIZE:
            o += datautils.pack(MC_VARINT, packet.data['port_tele_bound'])
        if act == mcdata.WB_SET_WARN_TIME or act == mcdata.WB_INITIALIZE:
            o += datautils.pack(MC_VARINT, packet.data['warn_time'])
        if act == mcdata.WB_SET_WARN_BLOCKS or act == mcdata.WB_INITIALIZE:
            o += datautils.pack(MC_VARINT, packet.data['warn_blocks'])
        return o

#Play  SERVER_TO_CLIENT 0x45 Title
@extension(mcdata.PLAY_STATE, mcdata.SERVER_TO_CLIENT, 0x45)
class ExtensionPSTC45:
    @staticmethod
    def decode_extra(packet, bbuff):
        act = packet.data['action']
        if act == mcdata.TL_TITLE or act == mcdata.TL_SUBTITLE:
            packet.data['text'] = datautils.unpack(MC_CHAT, bbuff)
        if act == mcdata.TL_TIMES:
            packet.data['fade_in'] = datautils.unpack(MC_INT, bbuff)
            packet.data['stay'] = datautils.unpack(MC_INT, bbuff)
            packet.data['fade_out'] = datautils.unpack(MC_INT, bbuff)
        return packet

    @staticmethod
    def encode_extra(packet):
        o = b''
        act = packet.data['action']
        if act == mcdata.TL_TITLE or act == mcdata.TL_SUBTITLE:
            o += datautils.pack(MC_CHAT, packet.data['text'])
        if act == mcdata.TL_TIMES:
            o += datautils.pack(MC_INT, packet.data['fade_in'])
            o += datautils.pack(MC_INT, packet.data['stay'])
            o += datautils.pack(MC_INT, packet.data['fade_out'])
        return o

#Play  CLIENT_TO_SERVER 0x02 Use Entity
@extension(mcdata.PLAY_STATE, mcdata.CLIENT_TO_SERVER, 0x02)
class ExtensionPCTS02:
    @staticmethod
    def decode_extra(packet, bbuff):
        if packet.data['action'] == mcdata.UE_INTERACT_AT:
            packet.data['target_x'] = datautils.unpack(MC_FLOAT, bbuff)
            packet.data['target_y'] = datautils.unpack(MC_FLOAT, bbuff)
            packet.data['target_z'] = datautils.unpack(MC_FLOAT, bbuff)
        return packet

    @staticmethod
    def encode_extra(packet):
        o = b''
        if packet.data['action'] == mcdata.UE_INTERACT_AT:
            o += datautils.pack(MC_FLOAT, packet.data['target_x'])
            o += datautils.pack(MC_FLOAT, packet.data['target_y'])
            o += datautils.pack(MC_FLOAT, packet.data['target_z'])
        return o

#ToDo: Set has_position True for encode based on prescence of 'block_loc'?
#Play  CLIENT_TO_SERVER 0x14 Tab-Complete
@extension(mcdata.PLAY_STATE, mcdata.CLIENT_TO_SERVER, 0x14)
class ExtensionPCTS14:
    @staticmethod
    def decode_extra(packet, bbuff):
        if packet.data['has_position'] == True:
            packet.data['block_loc'] = datautils.unpack(MC_POSITION, bbuff)
        return packet

    @staticmethod
    def encode_extra(packet):
        o = b''
        if packet.data['has_position'] == True:
            datautils.pack(MC_POSITION, packet.data['block_loc'])
        return o
