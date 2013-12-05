#Constantly Changing, just a plugin I use to debug whatever is broken atm
import sys
from spock.mcp import mcdata
from spock.utils import pl_announce

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
	def __init__(self, ploader, settings):
		for packet in mcdata.hashed_structs:
			ploader.reg_event_handler(packet, self.debug)
		ploader.reg_event_handler('tick', self.tick)

	def debug(self, name, packet):
		if packet.ident() == (mcdata.PLAY_STATE, mcdata.SERVER_TO_CLIENT, 0x26):
			packet.data['data'] = b''
		print(packet)

	def tick(self, name, data):
		#print('tick!')
		pass