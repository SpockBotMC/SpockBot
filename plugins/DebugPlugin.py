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
		self.physics = ploader.requires('Physics')
		self.timers = ploader.requires('Timers')
		ploader.reg_event_handler('w_block_update', self.block_test)
		#ploader.reg_event_handler('client_tick', self.timer_test)
		ploader.reg_event_handler('cl_health_update', self.clinfo_test)
		ploader.reg_event_handler('action_tick', self.walk_test)
		#self.timers.reg_event_timer(2, self.jump_test)

		self.old_time = 0

	def debug(self, name, packet):
		if packet.ident() == (mcdata.PLAY_STATE, mcdata.SERVER_TO_CLIENT, 0x26):
			packet.data['data'] = b''
			#print(packet)
		#print(packet)

	def walk_test(self, _, __):
		self.physics.walk(0)

	def jump_test(self):
		self.physics.jump()

	def clinfo_test(self, event, data):
		print('Health Update', data)

	def block_test(self, event, block):
		print('Block update at:', block['location'])
		print('New block data, id:', block['block_data']>>4, 'meta:',  block['block_data']&0x0F)

	def timer_test(self, _, __):
		new_time = int(round(time.time() * 1000))
		print(new_time - self.old_time)
		self.old_time = new_time
