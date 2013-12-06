#Constantly Changing, just a plugin I use to debug whatever is broken atm
import sys
import threading
from spock.mcmap import mapdata
from spock.mcp import mcdata
from spock.utils import pl_announce

class DebugPlugin:
	def __init__(self, ploader, settings):
		for packet in mcdata.hashed_structs:
			ploader.reg_event_handler(packet, self.debug)
		#ploader.reg_event_handler('tick', self.tick)
		#ploader.reg_event_handler('w_map_chunk', self.map)
		ploader.reg_event_handler('w_block_update', self.block_update)

	def debug(self, name, packet):
		if packet.ident() == (mcdata.PLAY_STATE, mcdata.SERVER_TO_CLIENT, 0x26):
			packet.data['data'] = b''
			#print(packet)
		#print(packet)

	def block_update(self, name, data):
		print('Block Updated!')
		print(
			'Block is:', mapdata.blocks[data.id]['display_name']+',', 
			'Biome:', mapdata.biomes[data.biome]['display_name']
		)
		print('Block Light:', str(data.block_light)+',', 'Sky Light:', data.sky_light)


	def map(self, name, data):
		print(data)

	def tick(self, name, data):
		print('tick!')
		print('Current threads:', threading.active_count())