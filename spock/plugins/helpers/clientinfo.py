"""
ClientInfo is a central plugin for recording data about the client
ex. Health, position, and some auxillary information like the player list
Plugins subscribing to ClientInfo and its events don't have to independently
track this information on their own.
"""

INV_CHEST      = 0
INV_WORKBENCH  = 1
INV_FURNACE    = 2
INV_DISPENSER  = 3
INV_ECHANTMENT = 4
INV_BREWING    = 5
INV_NPC        = 6
INV_BEACON     = 7
INV_ANVIL      = 8
INV_HOPPER     = 9
INV_DROPPER    = 10
INV_HORSE      = 11

from spock.utils import pl_announce
from spock.mcp import mcdata
from spock.mcp.mcdata import (
	FLG_XPOS_REL, FLG_YPOS_REL, FLG_ZPOS_REL, FLG_YROT_REL, FLG_XROT_REL
)

class Info(object):
	def set_dict(self, data):
		for key in data:
			if hasattr(self, key):
				setattr(self, key, data[key])

	def get_dict(self):
		return self.__dict__

	def __repr__(self):
		return repr(self.__dict__)

	def __str__(self):
		return str(self.__dict__)

class Position(Info):
	def __init__(self):
		self.x = 0.0
		self.y = 0.0
		self.z = 0.0

class GameInfo(Info):
	def __init__(self):
		self.level_type = 0
		self.dimension = 0
		self.gamemode = None
		self.difficulty = 0
		self.max_players = 0

class PlayerHealth(Info):
	def __init__(self):
		self.health = 20
		self.food = 20
		self.food_saturation = 5

class PlayerPosition(Position):
	def __init__(self):
		super(self.__class__, self).__init__()
		self.yaw = 0.0
		self.pitch = 0.0
		self.on_ground = False

class PlayerListItem(Info):
	def __init__(self):
		self.uuid = 0
		self.name = ''
		self.display_name = None
		self.ping = 0
		self.gamemode = 0

class ClientInfo:
	def __init__(self):
		self.eid = 0
		self.game_info = GameInfo()
		self.spawn_position = Position()
		self.health = PlayerHealth()
		self.position = PlayerPosition()
		self.player_list = []

	def reset(self):
		self.__init__()

@pl_announce('ClientInfo')
class ClientInfoPlugin:
	def __init__(self, ploader, settings):
		self.event = ploader.requires('Event')
		ploader.reg_event_handler(
			'PLAY<Join Game', self.handle_join_game
		)
		ploader.reg_event_handler(
			'PLAY<Spawn Position', self.handle_spawn_position
		)
		ploader.reg_event_handler(
			'PLAY<Update Health', self.handle_update_health
		)
		ploader.reg_event_handler(
			'PLAY<Player Position and Look', self.handle_position_update
		)
		ploader.reg_event_handler(
			'PLAY<Player List Item', self.handle_player_list
		)
		ploader.reg_event_handler(
			'disconnect', self.handle_disconnect
		)
		self.uuids = {}
		self.client_info = ClientInfo()
		ploader.provides('ClientInfo', self.client_info)

	#Login Request - Update client state info
	def handle_join_game(self, event, packet):
		self.client_info.eid = packet.data['eid']
		self.client_info.game_info.set_dict(packet.data)
		self.event.emit('cl_join_game', self.client_info.game_info)

	#Spawn Position - Update client Spawn Position state
	def handle_spawn_position(self, event, packet):
		self.client_info.spawn_position.set_dict(packet.data['location'])
		self.event.emit('cl_spawn_update', self.client_info.spawn_position)

	#Update Health - Update client Health state
	def handle_update_health(self, event, packet):
		self.client_info.health.set_dict(packet.data)
		self.event.emit('cl_health_update', self.client_info.health)
		if packet.data['health'] <= 0.0:
			self.event.emit('cl_death', self.client_info.health)

	#Player Position and Look - Update client Position state
	def handle_position_update(self, event, packet):
		f = packet.data['flags']
		p = self.client_info.position
		d = packet.data
		p.x = p.x + d['x'] if f&FLG_XPOS_REL else d['x']
		p.y = p.y + d['y'] if f&FLG_YPOS_REL else d['y']
		p.z = p.z + d['z'] if f&FLG_ZPOS_REL else d['z']
		p.yaw = p.yaw + d['yaw'] if f&FLG_YROT_REL else d['yaw']
		p.pitch = p.pitch + d['pitch'] if f&FLG_XROT_REL else d['pitch']
		self.event.emit('cl_position_update', self.client_info.position)

	#Player List Item - Update player list
	def handle_player_list(self, event, packet):
		act = packet.data['action']
		for pl in packet.data['player_list']:
			#Minecraft server doesn't send PL Adds and Updates in the correct
			#order, so just check for new uuid instead
			if pl['uuid'] not in self.uuids and act != mcdata.PL_REMOVE_PLAYER:
				item = PlayerListItem()
				item.set_dict(pl)
				self.client_info.player_list.append(item)
				self.uuids[pl['uuid']] = item
				self.event.emit('cl_add_player', item)
			elif pl['uuid'] in self.uuids and act != mcdata.PL_REMOVE_PLAYER:
				item = self.uuids[pl['uuid']]
				item.set_dict(pl)
				self.event.emit('cl_update_player', item)
			elif act == mcdata.PL_REMOVE_PLAYER:
				item = self.uuids[pl['uuid']]
				self.client_info.player_list.remove(item)
				del self.uuids[pl['uuid']]
				self.event.emit('cl_remove_player', item)

	def handle_disconnect(self, name, packet):
		self.client_info.reset()
