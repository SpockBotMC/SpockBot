#Constantly Changing, just a plugin I use to debug whatever is broken atm
import sys
import threading
from spock.mcmap import mapdata
from spock.mcp import mcdata
from spock.utils import pl_announce
import time

class DebugPlugin:
	def __init__(self, ploader, settings):
		#for packet in mcdata.hashed_structs:
		#	ploader.reg_event_handler(packet, self.debug)
		#ploader.reg_event_handler('tick', self.tick)
		#ploader.reg_event_handler('w_map_chunk', self.map)
		ploader.reg_event_handler('client_tick', self.timer_test)
		self.old_time = 0

	def debug(self, name, packet):
		if packet.ident() == (mcdata.PLAY_STATE, mcdata.SERVER_TO_CLIENT, 0x26):
			packet.data['data'] = b''
			#print(packet)
		#print(packet)

	def timer_test(self, _, __):
		new_time = int(round(time.time() * 1000))
		print(new_time - self.old_time)
		self.old_time = new_time
