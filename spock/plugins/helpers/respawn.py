"""
RespawnPlugin's scope is huge, only KeepAlivePlugin does more
"""

from spock.mcp import mcdata

class RespawnPlugin:
	def __init__(self, ploader, settings):
		self.net = ploader.requires('Net')
		if not ploader.requires('ClientInfo'):
			ploader.reg_event_handler(
				'PLAY<Update Health', self.handle_update_health_packet
			)
		else:
			ploader.reg_event_handler(
				'death', self.handle_death_event
			)

	#Update Health
	def handle_update_health_packet(self, name, packet):
		#You be dead
		if packet.data['health'] <= 0.0:
			self.net.push_packet(
				'PLAY>Client Status', {'action': mcdata.CL_STATUS_RESPAWN}
			)

	def handle_death_event(self, name, data):
		self.net.push_packet(
			'PLAY>Client Status', {'action': mcdata.CL_STATUS_RESPAWN}
		)
