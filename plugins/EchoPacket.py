from spock.mcp.mcdata import structs

class EchoPacketPlugin:
	def __init__(self, client, settings):
		client.register_dispatch(self.echopacket, *structs)

	def echopacket(self, packet):
		print(packet)