from spock.mcp.mcdata import hashed_structs
from spock.mcp import mcdata

class EchoPacketPlugin:
	def __init__(self, ploader, settings):
		for i in list(hashed_structs.keys()):
			ploader.reg_event_handler(i, self.echopacket)

	def echopacket(self, name, packet):
		if packet.ident() != (mcdata.PLAY_STATE, mcdata.SERVER_TO_CLIENT, 0x26):
			print(packet)
