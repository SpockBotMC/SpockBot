from spock.mcp.mcdata import hashed_structs

class EchoPacketPlugin:
	def __init__(self, ploader, settings):
		for i in list(hashed_structs.keys()):
			ploader.reg_event_handler(i, self.echopacket)

	def echopacket(self, name, packet):
		print(packet)
