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
		#You be dead
		print(packet.data['health'])
		if packet.data['health'] <= 0.0:
			self.net.push(mcpacket.Packet(
				ident = (mcdata.PLAY_STATE, mcdata.CLIENT_TO_SERVER, 0x16),
				data = {
					'action': mcdata.CL_STATUS_RESPAWN,
				}
			))
