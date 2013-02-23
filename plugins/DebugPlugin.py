#Constantly Changing, just a plugin I use to debug whatever is broken atm
import sys
from spock.mcp.mcdata import structs

class DebugPlugin:
	def __init__(self, client):
		self.client = client
		client.register_dispatch(self.debug, *structs)

	def debug(self, packet):
		if (packet.ident == 0xC9 
		or packet.ident == 0x03
		or packet.ident == 0xFF
		or packet.ident == 0x0D):
			sys.stdout.write(str(packet))
			#print packet
