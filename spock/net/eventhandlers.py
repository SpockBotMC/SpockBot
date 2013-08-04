import logging
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
	def __init__(self, client):
		self.client = client
		client.reg_event_handler([event for event in handles], self.handle_event)

	def handle_event(self, name, data):
		handles[name].handle(self.client, data)

#SOCKET_ERR - Socket Error has occured
@handle('SOCKET_ERR')
class handleERR:
	def handle(client, data):
		if client.sock_quit and not client.kill:
			print("Socket Error has occured, stopping...")
			client.kill = True
		utils.ResetClient(client)

#SOCKET_HUP - Socket has hung up
@handle('SOCKET_HUP')
class handleHUP:
	def handle(client, data):
		if client.sock_quit and not client.kill:
			print("Socket has hung up, stopping...")
			client.kill = True
		utils.ResetClient(client)

#SOCKET_RECV - Socket is ready to recieve data
@handle('SOCKET_RECV')
class handleSRECV:
	def handle(client, data):
		try:
			data = client.sock.recv(client.bufsize)
			client.rbuff.append(client.cipher.decrypt(data) if client.encrypted else data)
		except socket.error as error:
			logging.info(str(error))
		try:
			while True:
				client.rbuff.save()
				packet = mcpacket.read_packet(client.rbuff)
				client.emit(packet.ident, packet)
		except bound_buffer.BufferUnderflowException:
			client.rbuff.revert()

#SOCKET_SEND - Socket is ready to send data and Send buffer contains data to send
@handle('SOCKET_SEND')
class handleSEND:
	def handle(client, data):
		try:
			sent = client.sock.send(client.sbuff)
			client.sbuff = client.sbuff[sent:]
		except socket.error as error:
			logging.info(str(error))

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

#Keep Alive - Reflects data back to server
@handle(0x00)
class handle00(BasePacketHandle):
	@classmethod
	def ToClient(self, client, packet):
		packet.direction = mcdata.CLIENT_TO_SERVER
		client.push(packet)

#Login Request - Update client state info
@handle(0x01)
class handle01(BasePacketHandle):
	@classmethod
	def ToClient(self, client, packet):
		client.eid = packet.data['entity_id']
		del packet.data['entity_id']
		client.login_info = packet.data

#Time Update - Update client World Time state
@handle(0x04)
class handle04(BasePacketHandle):
	@classmethod
	def ToClient(self, client, packet):
		client.world_time = packet.data

#Spawn Position - Update client Spawn Position state
@handle(0x06)
class handle06(BasePacketHandle):
	@classmethod
	def ToClient(self, client, packet):
		client.spawn_position = packet.data

#Update Health - Update client Health state
@handle(0x08)
class handle08(BasePacketHandle):
	@classmethod
	def ToClient(self, client, packet):
		client.health = packet.data

#Respawn - Unload the World
@handle(0x09)
class handle09(BasePacketHandle):
	@classmethod
	def ToClient(self, client, packet):
		client.world = smpmap.World()

#Position Update Packets - Update client Position state
@handle(0x0A)
@handle(0x0B)
@handle(0x0C)
@handle(0x0D)
class PositionUpdate(BasePacketHandle):
	@classmethod
	def ToClient(self, client, packet):
		for key, value in packet.data.items():
			client.position[key] = value
		client.push(mcpacket.Packet(ident=0x0D, data = client.position))
	@classmethod
	def ToServer(self, client, packet):
		for key, value in packet.data.items():
			client.position[key] = value

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

#Player List Item - Update client Playerlist (not actually a list...)
@handle(0xC9)
class handleC9(BasePacketHandle):
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
@handle(0xFC)
class handleFC(BasePacketHandle):
	@classmethod
	def ToClient(self, client, packet):
		#Stage 5: Enable encryption and send Client Status
		client.enable_crypto(client.SharedSecret)
		client.push(mcpacket.Packet(ident = 0xCD, data = {
			'payload': 0,
			})
		)

#Encryption Key Request - Request for client to start encryption
@handle(0xFD)
class handleFD(BasePacketHandle):
	@classmethod
	def ToClient(self, client, packet):
		#Stage 3: Authenticate with session.minecraft.net
		pubkey = packet.data['public_key']
		if client.authenticated:
			serverid = utils.HashServerId(packet.data['server_id'], client.SharedSecret, pubkey)
			SessionResponse = utils.AuthenticateMinecraftSession(client.username, client.sessionid, serverid)
			print(SessionResponse)
			if (SessionResponse != 'OK'):
				logging.error('Session Authentication Failed, Response: %s', SessionResponse)
				client.auth_err = True
				return

		#Stage 4: Send an Encryption Response
		RSACipher = PKCS1_v1_5.new(RSA.importKey(pubkey))
		encryptedSanityToken = RSACipher.encrypt(packet.data['verify_token'])
		encryptedSharedSecret = RSACipher.encrypt(client.SharedSecret)
		client.push(mcpacket.Packet(ident = 0xFC, data = {
			'shared_secret': encryptedSharedSecret,
			'verify_token': encryptedSanityToken,
			})
		)

#Disconnect - Reset everything after a disconect
@handle(0xFF)
class handleFD(BasePacketHandle):
	@classmethod
	def ToClient(self, client, packet):
		utils.ResetClient(client)
