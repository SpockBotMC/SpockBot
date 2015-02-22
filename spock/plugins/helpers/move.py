"""
MovementPlugin provides a centralized plugin for controlling all outgoing
position packets so the client doesn't try to pull itself in a dozen directions.
Also provides very basic pathfinding
"""

from spock.utils import pl_announce
from spock.mcp import mcdata
from spock.utils import Vec3
import math

import logging
logger = logging.getLogger('spock')

class MovementCore:
	def __init__(self):
		self.move_location = None
	def move_to(self, x, y, z):
		self.move_location = Vec3(x, y, z)

@pl_announce('Movement')
class MovementPlugin:
	def __init__(self, ploader, settings):
		self.net = ploader.requires('Net')
		self.clinfo = ploader.requires('ClientInfo')
		self.physics = ploader.requires('Physics')
		ploader.reg_event_handler('client_tick', self.client_tick)
		ploader.reg_event_handler('action_tick', self.action_tick)
		ploader.reg_event_handler('cl_position_update', self.handle_position_update)
		ploader.reg_event_handler('phy_collision', self.handle_collision)
		self.movement = MovementCore()
		ploader.provides('Movement', self.movement)


	def client_tick(self, name, data):
		self.net.push_packet('PLAY>Player Position', self.clinfo.position.get_dict())

	def handle_position_update(self, name, data):
		self.net.push_packet('PLAY>Player Position and Look', data.get_dict())

	def handle_collision(self, name, data):
		if self.movement.move_location != None:
			self.physics.jump()

	def action_tick(self, name, data):
		self.do_pathfinding()

	def do_pathfinding(self):
		if self.movement.move_location != None:
			if self.movement.move_location.x == math.floor(self.clinfo.position.x) and self.movement.move_location.z == math.floor(self.clinfo.position.z):
				self.movement.move_location = None;
			else:
				dx = self.movement.move_location.x - self.clinfo.position.x
				dz = self.movement.move_location.z - self.clinfo.position.z
				deg = 0
				if abs(dx) >= abs(dz):
					#we should go along x
					if dx > 0:
						#go positive x
						deg = 90
					else:
						#go neg x
						deg = 270

				elif abs(dx) < abs(dz):
					#we should go along z
					if dz > 0:
						#go positive z
						deg = 0
					else:
						#go neg z
						deg = 180

				self.physics.walk(deg)
