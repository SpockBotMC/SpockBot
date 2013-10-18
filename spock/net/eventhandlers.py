import socket
from spock import utils, smpmap, bound_buffer
from spock.mcp import mcdata, mcpacket
from Crypto.Cipher import PKCS1_v1_5
from Crypto.PublicKey import RSA

handles = {}
def handle(ident):
	def inner(cl):
		handles[ident] = cl
		return cl
	return inner

class ClientEventHandlers:
	def __init__(self, pl_loader, settings):
		self.client = pl_loader.requires('Client')
		pl_loader.reg_event_handler([event for event in handles], self.handle_event)

	def handle_event(self, name, data):
		handles[name].handle(self.client, data)

class BasePacketHandle:
	@classmethod
	def handle(self, client, packet):
		if packet.direction == mcdata.SERVER_TO_CLIENT:
			self.ToClient(client, packet)
		elif packet.direction == mcdata.CLIENT_TO_SERVER:
			self.ToServer(client, packet)
		else:
			return 0
	@classmethod
	def ToClient(self, client, packet):
		pass
	@classmethod
	def ToServer(self, client, packet):
		pass

#Time Update - Update client World Time state
@handle(0x04)
class handle04(BasePacketHandle):
	@classmethod
	def ToClient(self, client, packet):
		client.world_time = packet.data

#Respawn - Unload the World
@handle(0x09)
class handle09(BasePacketHandle):
	@classmethod
	def ToClient(self, client, packet):
		client.world = smpmap.World()

class SpawnEntity(BasePacketHandle):
	@classmethod
	def ToClient(self, client, packet):
		eid = packet.data['entity_id']
		del packet.data['entity_id']
		client.entitylist[eid] = packet.data

#Chunk Data - Update client World state
@handle(0x33)
class handle33(BasePacketHandle):
	@classmethod
	def ToClient(self, client, packet):
		client.world.unpack_column(packet)

#Map Chunk Bulk - Update client World state
@handle(0x38)
class handle38(BasePacketHandle):
	@classmethod
	def ToClient(self, client, packet):
		client.world.unpack_bulk(packet)

#Disconnect - Reset everything after a disconect
@handle(0xFF)
class handleFD(BasePacketHandle):
	@classmethod
	def ToClient(self, client, packet):
		client.reset()
