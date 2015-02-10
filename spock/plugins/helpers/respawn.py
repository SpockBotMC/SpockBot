"""
RespawnPlugin's scope is huge, only KeepAlivePlugin does more
"""

from spock.mcp import mcdata

import logging
logger = logging.getLogger('spock')

class RespawnPlugin:
	def __init__(self, ploader, settings):
		self.net = ploader.requires('Net')
		ploader.requires('ClientInfo')
		ploader.reg_event_handler(
			'cl_death', self.handle_death
		)

	#You be dead
	def handle_death(self, name, data):
		self.net.push_packet(
			'PLAY>Client Status', {'action': mcdata.CL_STATUS_RESPAWN}
		)
