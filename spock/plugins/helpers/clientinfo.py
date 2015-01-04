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

class ClientInfo:
	def __init__(self):
		self.eid = 0
		self.game_info = {
			'level_type': 0,
			'gamemode': None,
			'difficulty': 0,
			'max_players': 0,
		}
		self.spawn_position = {
			'x': 0,
			'y': 0,
			'z': 0,
		}
		self.health = {
			'health': 20,
			'food': 20,
			'food_saturation': 5,
		}
		self.position = {
			'x': 0,
			'y': 0,
			'z': 0,
			'stance': 0,
			'yaw': 0,
			'pitch': 0,
			'on_ground': False,
		}
		self.player_list = {}

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
			'PLAY<Player Position and Look', self.handle_update_position
		)
		for event in 'PLAY<Disconnect', 'SOCKET_HUP', 'SOCKET_ERR':
			ploader.reg_event_handler(
				event, self.handle_disconnect
		)

		self.client_info = ClientInfo()
		ploader.provides('ClientInfo', self.client_info)

	#Login Request - Update client state info
	def handle_join_game(self, event, packet):
		self.client_info.eid = packet.data['eid']
		for key in self.client_info.game_info.keys():
			self.client_info.game_info[key] = packet.data[key]
		self.event.emit('cl_join_game', packet.data)

	#Spawn Position - Update client Spawn Position state
	def handle_spawn_position(self, event, packet):
		self.client_info.spawn_position = packet.data['location']
		self.event.emit('cl_spawn_update', packet.data['location'])

	#Update Health - Update client Health state
	def handle_update_health(self, name, packet):
		self.client_info.health = packet.data
		self.event.emit('cl_health_update', packet.data)

	#Player Position and Look - Update client Position state
	def handle_update_position(self, name, packet):
		f = packet.data['flags']
		p = self.client_info.position
		d = packet.data
		p['x'] = p['x'] + d['x'] if f&FLG_XPOS_REL else d['x']
		p['y'] = p['y'] + d['y'] if f&FLG_YPOS_REL else d['y']
		p['z'] = p['z'] + d['z'] if f&FLG_YPOS_REL else d['z']
		p['yaw'] = p['yaw'] + d['yaw'] if f&FLG_YROT_REL else d['yaw']
		p['pitch'] = p['pitch'] + d['pitch'] if f&FLG_XROT_REL else d['pitch']
		self.event.emit('cl_position_update', self.client_info.position)

	def handle_disconnect(self, name, packet):
		self.client_info.reset()
