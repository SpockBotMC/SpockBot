from spock.mcp.mcdata import structs

class EchoPacketPlugin:
	def __init__(self, client):
		for ident in structs:
			client.register_dispatch(self.echopacket, ident)
	def run(self):
		pass
	def echopacket(self, packet):
		print packet