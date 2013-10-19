#Constantly Changing, just a plugin I use to debug whatever is broken atm
import sys
from spock.mcp.mcdata import structs
from spock.net.cflags import cflags
from spock.plugins.plutils import pl_announce

@pl_announce('dummytest1')
class TestRequire1:
	def __init__(self, pl_loader, settings):
		print('dummytest1 loaded, requires provided:', pl_loader.requires('dummytest3'))
		pl_loader.provides('dummytest1', self)

@pl_announce('dummytest3')
class TestRequire3:
	def __init__(self, pl_loader, settings):
		pl_loader.provides('dummytest3', self)
		print('dummytest3 loaded')

class DebugPlugin:
	def __init__(self, pl_loader, settings):
		print('DebugPlugin loaded, requires provided:', pl_loader.requires('dummytest1'))
		pl_loader.reg_event_handler((0xC9, 0x03, 0xFF, 0x0D), self.debug)

	def debug(self, name, packet):
		if (packet.ident == 0xC9 
		or packet.ident == 0x03
		or packet.ident == 0xFF
		or packet.ident == 0x0D):
			print(packet)