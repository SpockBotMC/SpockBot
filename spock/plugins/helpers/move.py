"""
MovementPlugin provides a centralized plugin for controlling all outgoing
position packets so the client doesn't try to pull itself in a dozen directions.
It is planned to provide basic pathfinding and coordinate with the physics
plugin to implement SMP-compliant movement
"""

from spock.mcp import mcdata

class MovementPlugin:
	def __init__(self, ploader, settings):
		self.net = ploader.requires('Net')
		self.clinfo = ploader.requires('ClientInfo')
		if not self.clinfo:
			#TODO: Make this a soft dependency?
			print("MovementPlugin requires ClientInfo, bailing out")
			return
		ploader.reg_event_handler(
			'client_tick', self.client_tick
		)
		ploader.reg_event_handler(
			'cl_position_update', self.handle_position_update
		)

	def client_tick(self, name, data):
		self.net.push_packet(
			'PLAY>Player Position', self.clinfo.position.getDict()
		)

	def handle_position_update(self, name, data):
		self.net.push_packet(
			'PLAY>Player Position and Look', data.getDict()
		)
