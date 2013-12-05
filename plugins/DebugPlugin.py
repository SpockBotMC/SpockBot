#Constantly Changing, just a plugin I use to debug whatever is broken atm
import sys
import threading
from spock.mcp import mcdata
from spock.utils import pl_announce

class DebugPlugin:
	def __init__(self, ploader, settings):
		for packet in mcdata.hashed_structs:
			ploader.reg_event_handler(packet, self.debug)
		#ploader.reg_event_handler('tick', self.tick)
		#ploader.reg_event_handler('map_chunk_bulk', self.map)

	def debug(self, name, packet):
		if packet.ident() == (mcdata.PLAY_STATE, mcdata.SERVER_TO_CLIENT, 0x26):
			packet.data['data'] = b''
			print(packet)
		print(packet)

	def map(self, name, data):
		print(data)

	def tick(self, name, data):
		print('tick!')
		print('Current threads:', threading.active_count())