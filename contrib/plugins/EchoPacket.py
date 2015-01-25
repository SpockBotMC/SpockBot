from spock.mcp.mcdata import hashed_structs
from spock.mcp import mcdata

BLACKLIST = ['PLAY<Map Chunk Bulk', 'PLAY<Chunk Data', 'PLAY>Player Position']
		#'PLAY<Entity Velocity', 'PLAY<Entity Relative Move', 'PLAY<Entity Look and Relative Move', 'PLAY<Entity Head Look', 'PLAY<Entity Look', 'PLAY<Entity Metadata', 'PLAY<Entity Teleport']

class EchoPacketPlugin:
	def __init__(self, ploader, settings):
		for i in list(hashed_structs.keys()):
			ploader.reg_event_handler(i, self.echopacket)

	def echopacket(self, name, packet):
		#Dont print Chunk Data and Map Chunk Bulk
		if packet.str_ident not in BLACKLIST:
			print(packet)
