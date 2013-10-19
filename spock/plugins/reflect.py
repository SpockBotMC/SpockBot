from spock.mcp import mcdata, mcpacket

class ReflectPlugin:
	def __init__(self, ploader, settings):
		self.net = ploader.requires('Net')
		self.client_info = ploader.requires('ClientInfo')
		ploader.reg_event_handler(0x00, self.handle00)
		ploader.reg_event_handler(
			(0x0A, 0x0B, 0x0C, 0x0D), 
			self.handle_position_update
		)

	#Keep Alive - Reflects data back to server
	def handle00(self, name, packet):
		if packet.direction == mcdata.SERVER_TO_CLIENT:
			packet.direction = mcdata.CLIENT_TO_SERVER
			self.net.push(packet)

	#Position Update Packets - Reflect new position back to server
	def handle_position_update(self, name, packet):
		if packet.direction == mcdata.SERVER_TO_CLIENT:
			self.net.push(mcpacket.Packet(
				ident = 0x0D, 
				data = self.client_info.position
			))