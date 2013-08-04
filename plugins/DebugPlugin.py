#Constantly Changing, just a plugin I use to debug whatever is broken atm
import sys
from spock.mcp.mcdata import structs
from spock.net.cflags import cflags

class DebugPlugin:
	def __init__(self, client, settings):
		self.client = client
		client.reg_event_handler((0xC9, 0x03, 0xFF, 0x0D), self.debug)

	def debug(self, packet):
		if (packet.ident == 0xC9 
		or packet.ident == 0x03
		or packet.ident == 0xFF
		or packet.ident == 0x0D):
			print(packet)