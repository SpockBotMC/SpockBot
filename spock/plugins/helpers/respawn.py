from spock.mcp import mcdata, mcpacket

class RespawnPlugin:
	def __init__(self, ploader, settings):
		self.net = ploader.requires('Net')
		ploader.reg_event_handler(
			(mcdata.PLAY_STATE, mcdata.SERVER_TO_CLIENT, 0x06), 
			self.handle_update_health
		)

	#Update Health
	def handle_update_health(self, name, packet):
		print(packet)