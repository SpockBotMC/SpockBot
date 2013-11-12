from spock.mcp import mcdata, mcpacket

class KeepalivePlugin:
	def __init__(self, ploader, settings):
		self.net = ploader.requires('Net')
		ploader.reg_event_handler(0x00, self.handle00)

	#Keep Alive - Reflects data back to server
	def handle00(self, name, packet):
		if packet.direction == mcdata.SERVER_TO_CLIENT:
			packet.direction = mcdata.CLIENT_TO_SERVER
			self.net.push(packet)