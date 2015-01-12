from spock.mcp.mcdata import hashed_structs
from spock.mcp import mcdata

class EchoPacketPlugin:
	def __init__(self, ploader, settings):
		for i in list(hashed_structs.keys()):
			ploader.reg_event_handler(i, self.echopacket)

	def echopacket(self, name, packet):
		#Dont print Chunk Data and Map Chunk Bulk
		if packet.str_ident != 'PLAY<Map Chunk Bulk' and packet.str_ident != 'PLAY<Chunk Data' and packet.str_ident != 'PLAY>Player Position':
			print(packet)
