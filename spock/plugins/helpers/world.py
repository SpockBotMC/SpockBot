"""
Provides a very raw (but very fast) world map for use by plugins.
Plugins interested in a more comprehensive world map view will eventually be
able to use smpmap2 to interpret data from the world plugin and its events.
Planned to provide light level interpretation based on sky light and time of day
"""

from spock.utils import pl_announce
from spock.mcmap import smpmap
from spock.mcp import mcdata
import math

#TODO: Track Entities?

class WorldData(smpmap.Dimension):
	def __init__(self, dimension = mcdata.SMP_OVERWORLD):
		super().__init__(dimension)
		self.age = 0
		self.time_of_day = 0

	def update_time(self, data):
		self.age = data['world_age']
		self.time_of_day = data['time_of_day']

	#TODO: Check if block is solid, not just check for air
	def get_floor(self, x, y, z):
		x, y, z = math.floor(x), math.floor(y), math.floor(z)
		backup_y = y
		block_id, _ = self.get_block(x, y, z)
		while(block_id == 0 and y > 0):
			y -= 1
			block_id, _ = self.get_block(x, y, z)
		if y < 0:
			return backup_y
		return y + 1

	def new_dimension(self, dimension):
		super().__init__(dimension)

	def reset(self):
		self.__init__(self.dimension)

@pl_announce('World')
class WorldPlugin:
	def __init__(self, ploader, settings):
		self.world = WorldData()
		self.event = ploader.requires('Event')
		ploader.provides('World', self.world)
		packets = (0x01, 0x07, 0x03, 0x21, 0x22, 0x23, 0x26)
		handlers = (
			self.handle_new_dimension, self.handle_new_dimension,
			self.handle03, self.handle21, self.handle22, self.handle23,
			self.handle26
		)
		for i in range(len(packets)):
			ploader.reg_event_handler(
				(mcdata.PLAY_STATE, mcdata.SERVER_TO_CLIENT, packets[i]),
				handlers[i]
			)
		ploader.reg_event_handler('disconnect', self.handle_disconnect)

	#Time Update - Update World Time
	def handle03(self, name, packet):
		self.world.update_time(packet.data)
		self.event.emit('w_time_update', packet.data)

	#Join Game/Respawn - New Dimension
	def handle_new_dimension(self, name, packet):
		self.world.new_dimension(packet.data['dimension'])
		self.event.emit('w_new_dimension', packet.data['dimension'])

	#Chunk Data - Update World state
	def handle21(self, name, packet):
		self.world.unpack_column(packet.data)

	#Multi Block Change - Update multiple blocks
	def handle22(self, name, packet):
		chunk_x = packet.data['chunk_x']*16
		chunk_z = packet.data['chunk_z']*16
		for block in packet.data['blocks']:
			x = block['x'] + chunk_x
			z = block['z'] + chunk_z
			y = block['y']
			self.world.set_block(x, y, z, data = block['block_data'])
			self.event.emit('w_block_update', {
				'location': {
					'x': x,
					'y': y,
					'z': z,
				},
				'block_data': block['block_data'],
			})

	#Block Change - Update a single block
	def handle23(self, name, packet):
		p = packet.data['location']
		block_data = packet.data['block_data']
		self.world.set_block(p['x'], p['y'], p['z'], data = block_data)
		self.event.emit('w_block_update', packet.data)

	#Map Chunk Bulk - Update World state
	def handle26(self, name, packet):
		self.world.unpack_bulk(packet.data)

	def handle_disconnect(self, name, data):
		self.world.reset()
		self.event.emit('w_world_reset')
