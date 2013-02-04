from spock.mcp.mcdata import structs

class EchoPacketPlugin:
	def __init__(self, client):
		for ident in structs:
			client.register_dispatch(self, ident)
	def run(self):
		pass
	def dispatch_packet(self, packet):
		print packet