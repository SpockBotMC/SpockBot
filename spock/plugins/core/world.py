from spock.plugins.plutils import pl_announce
from spock.mcmap import smpmap

#TODO: Track Entities, real world API

class WorldData:
	def __init__(self):
		self.map = smpmap.World()
		self.age = 0
		self.time_of_day = 0
		self.entity_list = {}

	def unload(self):
		self.map = smpmap.World()

	def reset(self):
		self.__init__()

@pl_announce('World')
class WorldPlugin:
	def __init__(self, ploader, settings):
		self.world = WorldData()
		ploader.provides('World', self.world)
		ploader.reg_event_handler(0x04, self.handle04)
		ploader.reg_event_handler(0x09, self.handle09)
		#ploader.reg_event_handler(0x33, self.handle33)
		#ploader.reg_event_handler(0x38, self.handle38)
		ploader.reg_event_handler(
			(0xFF, 'SOCKET_ERR', 'SOCKET_HUP'),
			self.handle_disconnect
		)

	#Time Update - Update World Time
	def handle04(self, name, packet):
		self.world.age = packet.data['world_age']
		self.world.time_of_day = packet.data['time_of_day']

	#Respawn - Unload the World
	def handle09(self, name, packet):
		self.world.unload()

	#Chunk Data - Update client World state
	def handle33(self, name, packet):
		self.world.map.unpack_column(packet.data)

	#Map Chunk Bulk - Update client World state
	def handle38(self, name, packet):
		self.world.map.unpack_bulk(packet.data)

	def handle_disconnect(self, name, data):
		self.world.reset()
