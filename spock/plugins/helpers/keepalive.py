from spock.mcp import mcdata, mcpacket

class KeepalivePlugin:
	def __init__(self, ploader, settings):
		self.net = ploader.requires('Net')
		ploader.reg_event_handler(
			(mcdata.PLAY_STATE, mcdata.SERVER_TO_CLIENT, 0x00),
			self.handle00
		)

	#Keep Alive - Reflects data back to server
	def handle00(self, name, packet):
		packet.new_ident((mcdata.PLAY_STATE, mcdata.CLIENT_TO_SERVER, 0x00))
		self.net.push(packet)
