"""
ClientInfo is a central plugin for recording data about the client
ex. Health, position, and some auxillary information like the player list
Plugins subscribing to ClientInfo and its events don't have to independently
track this information on their own.
"""

from spock.utils import pl_announce
from spock.mcp.mcdata import (
	FLG_XPOS_REL, FLG_YPOS_REL, FLG_ZPOS_REL, FLG_YROT_REL, FLG_XROT_REL
)

class Info:
	def getDict(self):
		return self.__dict__
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
		self.yaw = 0.0
		self.pitch = 0.0
		self.on_ground = False

class Inventory(Info):
	def __init__(self):
		self.slots = []

class ClientInfo:
	def __init__(self):
		self.eid = 0
		self.game_info = GameInfo()
		self.spawn_position = Position()
		self.health = PlayerHealth()
		self.position = PlayerPosition() 
		self.player_list = {}
	
	def update_data(self, obj, data):
		for key in data:
			if hasattr(obj, key):
				setattr(obj, key, data[key])


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
			'disconnect', self.handle_disconnect
		)

		self.client_info = ClientInfo()
		ploader.provides('ClientInfo', self.client_info)

	#Login Request - Update client state info
	def handle_join_game(self, event, packet):
		self.client_info.eid = packet.data['eid']
		self.client_info.update_data(self.client_info.game_info, packet.data)
		self.event.emit('cl_join_game', self.client_info.game_info)

	#Spawn Position - Update client Spawn Position state
	def handle_spawn_position(self, event, packet):
		self.client_info.update_data(self.client_info.spawn_position, packet.data['location'])
		self.event.emit('cl_spawn_update', self.client_info.spawn_position)

	#Update Health - Update client Health state
	def handle_update_health(self, name, packet):
		self.client_info.update_data(self.client_info.health, packet.data)
		self.event.emit('cl_health_update', self.client_info.health)
		if packet.data['health'] <= 0.0:
			self.event.emit('death', self.client_info.health)

	#Player Position and Look - Update client Position state
	def handle_position_update(self, name, packet):
		f = packet.data['flags']
		p = self.client_info.position
		d = packet.data
		p.x = p.x + d['x'] if f&FLG_XPOS_REL else d['x']
		p.y = p.y + d['y'] if f&FLG_YPOS_REL else d['y']
		p.z = p.z + d['z'] if f&FLG_YPOS_REL else d['z']
		p.yaw = p.yaw + d['yaw'] if f&FLG_YROT_REL else d['yaw']
		p.pitch = p.pitch + d['pitch'] if f&FLG_XROT_REL else d['pitch']
		self.event.emit('cl_position_update', self.client_info.position)

	def handle_disconnect(self, name, packet):
		self.client_info.reset()
