#Constantly Changing, just a plugin I use to debug whatever is broken atm
import sys
from spock.mcp.mcdata import structs
from spock.net.cflags import cflags

class DebugPlugin:
	def __init__(self, client):
		self.client = client
		client.register_dispatch(self.debug, *structs)
		client.register_handler(self.dying, cflags['KILL_EVENT'])

	def dying(self, *args):
		print "I'm dying!"

	def debug(self, packet):
		if (packet.ident == 0xC9 
		or packet.ident == 0x03
		or packet.ident == 0xFF
		or packet.ident == 0x0D):
			print packet