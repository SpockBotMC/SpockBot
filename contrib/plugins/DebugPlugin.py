#Constantly Changing, just a plugin I use to debug whatever is broken atm
import sys
import threading
from spock.mcmap import mapdata
from spock.mcp import mcdata
from spock.utils import pl_announce, mapshort2id
import time

class DebugPlugin:
	def __init__(self, ploader, settings):
		#for packet in mcdata.hashed_structs:
		#	ploader.reg_event_handler(packet, self.debug)
		self.physics = ploader.requires('Physics')
		self.timers = ploader.requires('Timers')
		ploader.reg_event_handler('w_block_update', self.block_test)
		#ploader.reg_event_handler('client_tick', self.timer_test)
		ploader.reg_event_handler('cl_health_update', self.clinfo_test)
		ploader.reg_event_handler('action_tick', self.walk_test)
		self.timers.reg_event_timer(2, self.jump_test)

		self.old_time = 0

	def debug(self, name, packet):
		if packet.str_ident == 'PLAY<Map Chunk Bulk':
			packet.data['data'] = b''
			#print(packet)
		#print(packet)

	def walk_test(self, _, __):
		self.physics.walk(0)

	def jump_test(self):
		self.physics.jump()

	def clinfo_test(self, event, data):
		print('Health Update:', data)

	def block_test(self, event, blockdata):
		block_id, meta = mapshort2id(blockdata['block_data'])
		block = mapdata.get_block(block_id, meta)
		print('Block update at:', blockdata['location'])
		print('New block data:', block.display_name if block else None)

	def timer_test(self, _, __):
		new_time = int(round(time.time() * 1000))
		print(new_time - self.old_time)
		self.old_time = new_time
