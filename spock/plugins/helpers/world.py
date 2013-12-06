from spock.utils import pl_announce
from spock.mcmap import smpmap2
from spock.mcp import mcdata

#World loading relies pretty heavily on threading
#Here be dragons, be careful playing with this one

#TODO: Track Entities?

class WorldData:
	def __init__(self):
		self.map = smpmap2.World()
		self.age = 0
		self.time_of_day = 0

	def unload(self):
		self.map = smpmap2.World()

	def reset(self):
		self.__init__()

@pl_announce('World')
class WorldPlugin:
	def __init__(self, ploader, settings):
		self.world = WorldData()
		self.new_keys = []
		self.available_keys = []
		self.block_queue = []
		self.event = ploader.requires('Event')
		self.thread_pool = ploader.requires('ThreadPool')
		ploader.provides('World', self.world)
		ploader.reg_event_handler('tick', self.tick)
		packets = (0x03, 0x07, 0x21, 0x22, 0x23, 0x26)
		handlers = (self.handle03, self.handle07, self.handle21,
			self.handle22, self.handle23, self.handle26
		)
		for i in range(len(packets)):
			ploader.reg_event_handler(
				(mcdata.PLAY_STATE, mcdata.SERVER_TO_CLIENT, packets[i]), 
				handlers[i]
			)
		for i in 'SOCKET_ERR', 'SOCKET_HUP':
			ploader.reg_event_handler(
				i, self.handle_disconnect
			)

	def tick(self, name, data):
		for key in self.new_keys:
			self.event.emit('w_map_chunk', key)
			self.new_keys.remove(key)
		for block in self.block_queue:
			if (block['x']//16, block['z']//16) in self.available_keys:
				o = self.world.map.put(
					block['x'], block['y'], block['z'], block
				)
				self.block_queue.remove(block)
				self.event.emit('w_block_update', o)

	@staticmethod
	def async_column_loader(world, new_keys, available_keys, data):
		key = world.map.unpack_column(data)
		new_keys.append(key)
		available_keys.append(key)

	@staticmethod
	def async_bulk_loader(world, new_keys, available_keys, data):
		keys = world.map.unpack_bulk(data)
		new_keys.extend(keys)
		available_keys.extend(keys)

	#Time Update - Update World Time
	def handle03(self, name, packet):
		self.world.age = packet.data['world_age']
		self.world.time_of_day = packet.data['time_of_day']
		self.event.emit('w_time_update')

	#Respawn - Unload the World
	def handle07(self, name, packet):
		self.world.unload()
		self.new_keys = []
		self.available_keys = []
		self.block_queue = []
		self.event.emit('w_map_unload')

	#Chunk Data - Update World state
	#Probably could be done synchronously, but no harm using async
	def handle21(self, name, packet):
		self.thread_pool.submit(
			self.async_column_loader, self.world, 
			self.new_keys, self.available_keys, packet.data
		)

	#Multi Block Change - Update multiple blocks
	def handle22(self, name, packet):
		for block in packet.data['blocks']:
			if (block['x']//16, block['z']//16) in self.available_keys:
				o = self.world.map.put(
					block['x'], block['y'], block['z'], block
				)
				self.event.emit('w_block_update', o)
			else:
				self.block_queue.append(block)

	#Block Change - Update a single block
	def handle23(self, name, packet):
		block = packet.data
		if (block['x']//16, block['z']//16) in self.available_keys:
			o = self.world.map.put(
				block['x'], block['y'], block['z'], block
			)
			self.event.emit('w_block_update', o)
		else:
			self.block_queue.append(block)

	#Map Chunk Bulk - Update World state
	#Too slow to do synchronously
	def handle26(self, name, packet):
		self.thread_pool.submit(
			self.async_bulk_loader, self.world, 
			self.new_keys, self.available_keys, packet.data
		)

	def handle_disconnect(self, name, data):
		self.world.reset()
		self.new_keys = []
		self.available_keys = []
		self.block_queue = []
		self.event.emit('w_world_reset')
