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
		ploader.reg_event_handler('w_block_update', self.block_test)
		#ploader.reg_event_handler('client_tick', self.timer_test)
		self.old_time = 0

	def debug(self, name, packet):
		if packet.ident() == (mcdata.PLAY_STATE, mcdata.SERVER_TO_CLIENT, 0x26):
			packet.data['data'] = b''
			#print(packet)
		#print(packet)

	def block_test(self, event, block):
		print('Block update at:', block['location'])
		print('New block data:', block['block_data'])

	def timer_test(self, _, __):
		new_time = int(round(time.time() * 1000))
		print(new_time - self.old_time)
		self.old_time = new_time
