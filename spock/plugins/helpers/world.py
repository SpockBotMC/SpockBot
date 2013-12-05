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
		ploader.provides('World', self.world)
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

	#Time Update - Update World Time
	def handle03(self, name, packet):
		self.world.age = packet.data['world_age']
		self.world.time_of_day = packet.data['time_of_day']

	#Respawn - Unload the World
	def handle07(self, name, packet):
		self.world.unload()

	#Chunk Data - Update client World state
	def handle21(self, name, packet):
		self.world.map.unpack_column(packet.data)

	#Map Chunk Bulk - Update client World state
	def handle26(self, name, packet):
		self.world.map.unpack_bulk(packet.data)

	def handle_disconnect(self, name, data):
		self.world.reset()
