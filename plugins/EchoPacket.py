from spock.mcp.mcdata import structs

class EchoPacketPlugin:
	def __init__(self, ploader, settings):
		ploader.reg_event_handler(list(structs.keys()), self.echopacket)

	def echopacket(self, name, packet):
		print(packet)