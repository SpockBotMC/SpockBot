import logging
from spock import utils
from spock.mcp import mcdata, mcpacket
from spock.net.cflags import cflags
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
		client.push(mcpacket.Packet(ident = 0x00, data = {
			'value': packet.data['value']
			})
		)

#Position Update Packets - Update client Position state
@phandle(0x0A)
@phandle(0x0B)
@phandle(0x0C)
@phandle(0x0D)
class PositionUpdate(BaseHandle):
	@classmethod
	def ToClient(self, client, packet):
		for key in packet.data:
			client.position[key] = packet.data[key]
		client.flags += cflags['POS_UPDT']
	ToServer = ToClient

#Chunk Data - Update client World state
@phandle(0x33)
class handle33(BaseHandle):
	@classmethod
	def ToClient(self, client, packet):
		client.flags += cflags['WLD_UPDT']|cflags['BLK_UPDT']

#Map Chunk Bulk - Update client World state
@phandle(0x38)
class handle38(BaseHandle):
	@classmethod
	def ToClient(self, client, packet):
		client.flags += cflags['WLD_UPDT']|cflags['BLK_UPDT']

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
		serverid = utils.HashServerId(packet.data['server_id'], client.SharedSecret, pubkey)
		SessionResponse = utils.AuthenticateMinecraftSession(client.username, client.sessionid, serverid)
		if (SessionResponse != 'OK'):
			logging.error('Session Authentication Failed, Response: %s', SessionResponse)
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