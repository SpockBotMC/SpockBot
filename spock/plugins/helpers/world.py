from spock.utils import pl_announce
from spock.mcmap import smpmap2
from spock.mcp import mcdata

#TODO: Track Entities, real world API

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
		self.bulk_keys = []
		self.column_keys = []
		self.event = ploader.requires('Event')
		self.thread_pool = ploader.requires('ThreadPool')
		ploader.provides('World', self.world)
		ploader.reg_event_handler('tick', self.tick)
		ploader.reg_event_handler(
			(mcdata.PLAY_STATE, mcdata.SERVER_TO_CLIENT, 0x03),
			self.handle03
		)
		ploader.reg_event_handler(
			(mcdata.PLAY_STATE, mcdata.SERVER_TO_CLIENT, 0x07),
			self.handle07
		)
		ploader.reg_event_handler(
			(mcdata.PLAY_STATE, mcdata.SERVER_TO_CLIENT, 0x21),
			self.handle21
		)
		ploader.reg_event_handler(
			(mcdata.PLAY_STATE, mcdata.SERVER_TO_CLIENT, 0x26),
			self.handle26
		)
		for i in 'SOCKET_ERR', 'SOCKET_HUP':
			ploader.reg_event_handler(
				i, self.handle_disconnect
			)

	def tick(self, name, data):
		for keys in self.bulk_keys:
			self.event.emit('w_map_chunk_bulk', keys)
			self.bulk_keys.remove(keys)
		for key in self.column_keys:
			self.event.emit('w_map_chunk_column', key)
			self.column_keys.remove(key)

	def async_column_loader(self, data):
		key = self.world.map.unpack_column(data)
		self.column_keys.append(key)

	def async_bulk_loader(self, data):
		keys = self.world.map.unpack_bulk(data)
		self.bulk_keys.append(keys)

	#Time Update - Update World Time
	def handle03(self, name, packet):
		self.world.age = packet.data['world_age']
		self.world.time_of_day = packet.data['time_of_day']
		self.event.emit('w_time_update')

	#Respawn - Unload the World
	def handle07(self, name, packet):
		self.world.unload()
		self.event.emit('w_map_unload')

	#Chunk Data - Update World state
	#Probably could be done synchronously, but no harm using async
	def handle21(self, name, packet):
		self.thread_pool.submit(self.async_column_loader, packet.data)

	#Map Chunk Bulk - Update World state
	#Too slow to do synchronously
	def handle26(self, name, packet):
		self.thread_pool.submit(self.async_bulk_loader, packet.data)

	def handle_disconnect(self, name, data):
		self.world.reset()
		self.event.emit('w_world_reset')
