import logging
import socket
from spock import utils, smpmap
from spock.mcp import mcdata, mcpacket
from Crypto.Cipher import PKCS1_v1_5
from Crypto.PublicKey import RSA

phandles = {}
def phandle(ident):
	def inner(cl):
		phandles[ident] = cl
		return cl
	return inner

class BaseHandle:
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

#Keep Alive - Reflects data back to server
@phandle(0x00)
class handle00(BaseHandle):
	@classmethod
	def ToClient(self, client, packet):
		packet.direction = mcdata.CLIENT_TO_SERVER
		client.push(packet)

#Login Request - Update client state info
@phandle(0x01)
class handle01(BaseHandle):
	@classmethod
	def ToClient(self, client, packet):
		client.eid = packet.data['entity_id']
		del packet.data['entity_id']
		client.login_info = packet.data

#Time Update - Update client World Time state
@phandle(0x04)
class handle04(BaseHandle):
	@classmethod
	def ToClient(self, client, packet):
		client.world_time = packet.data

#Spawn Position - Update client Spawn Position state
@phandle(0x06)
class handle06(BaseHandle):
	@classmethod
	def ToClient(self, client, packet):
		client.spawn_position = packet.data

#Update Health - Update client Health state
@phandle(0x08)
class handle08(BaseHandle):
	@classmethod
	def ToClient(self, client, packet):
		client.health = packet.data

#Respawn - Unload the World
@phandle(0x09)
class handle09(BaseHandle):
	@classmethod
	def ToClient(self, client, packet):
		client.world = smpmap.World()

#Position Update Packets - Update client Position state
@phandle(0x0A)
@phandle(0x0B)
@phandle(0x0C)
@phandle(0x0D)
class PositionUpdate(BaseHandle):
	@classmethod
	def ToClient(self, client, packet):
		for key, value in packet.data.iteritems():
			client.position[key] = value
		client.push(mcpacket.Packet(ident=0x0D, data = client.position))
	@classmethod
	def ToServer(self, client, packet):
		for key, value in packet.data.iteritems():
			client.position[key] = value

class SpawnEntity(BaseHandle):
	@classmethod
	def ToClient(self, client, packet):
		eid = packet.data['entity_id']
		del packet.data['entity_id']
		client.entitylist[eid] = packet.data

#Chunk Data - Update client World state
@phandle(0x33)
class handle33(BaseHandle):
	@classmethod
	def ToClient(self, client, packet):
		client.world.unpack_column(packet)

#Map Chunk Bulk - Update client World state
@phandle(0x38)
class handle38(BaseHandle):
	@classmethod
	def ToClient(self, client, packet):
		client.world.unpack_bulk(packet)

#Player List Item - Update client Playerlist (not actually a list...)
@phandle(0xC9)
class handleC9(BaseHandle):
	@classmethod
	def ToClient(self, client, packet):
		name = packet.data['player_name']
		if packet.data['online']:
			client.playerlist[name] = packet.data['ping']
		else:
			try:
				del client.playerlist[name]
			except KeyError:
				logging.error('Tried to remove %s from playerlist, but player did not exist', name)

#Encryption Key Response - Signals encryption was successful, ready to spawn
@phandle(0xFC)
class handleFC(BaseHandle):
	@classmethod
	def ToClient(self, client, packet):
		#Stage 5: Enable encryption and send Client Status
		client.enable_crypto(client.SharedSecret)
		client.push(mcpacket.Packet(ident = 0xCD, data = {
			'payload': 0,
			})
		)

#Encryption Key Request - Request for client to start encryption
@phandle(0xFD)
class handleFD(BaseHandle):
	@classmethod
	def ToClient(self, client, packet):
		#Stage 3: Authenticate with session.minecraft.net
		pubkey = packet.data['public_key']
		if client.authenticated:
			serverid = utils.HashServerId(packet.data['server_id'], client.SharedSecret, pubkey)
			SessionResponse = utils.AuthenticateMinecraftSession(client.username, client.sessionid, serverid)
			if (SessionResponse != 'OK'):
				logging.error('Session Authentication Failed, Response: %s', SessionResponse)
				client.auth_err = True
				return

		#Stage 4: Send an Encryption Response
		RSACipher = PKCS1_v1_5.new(RSA.importKey(pubkey))
		encryptedSanityToken = RSACipher.encrypt(str(packet.data['verify_token']))
		encryptedSharedSecret = RSACipher.encrypt(str(client.SharedSecret))
		client.push(mcpacket.Packet(ident = 0xFC, data = {
			'shared_secret': encryptedSharedSecret,
			'verify_token': encryptedSanityToken,
			})
		)

#Disconnect - Reset everything after a disconect
@phandle(0xFF)
class handleFD(BaseHandle):
	@classmethod
	def ToClient(self, client, packet):
		utils.ResetClient(client)
