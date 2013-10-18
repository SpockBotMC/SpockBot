from Crypto.Cipher import PKCS1_v1_5
from Crypto.PublicKey import RSA
from spock import utils
from spock.mcp import mcdata, mcpacket

class AuthPlugin:
	def __init__(self, ploader, settings):
		self.client = ploader.requires('Client')
		ploader.reg_event_handler(0xFD, self.handleFD)
		ploader.reg_event_handler(0xFC, self.handleFC)



	#Encryption Key Response - Signals encryption was successful, ready to spawn
	def handleFC(self, name, packet):
		if packet.direction == mcdata.SERVER_TO_CLIENT:
			self.client.enable_crypto(self.client.SharedSecret)
			self.client.push(mcpacket.Packet(ident = 0xCD, data = {
				'payload': 0,
			}))

	#Encryption Key Request - Request for client to start encryption
	def handleFD(self, name, packet):
		pubkey = packet.data['public_key']
		if self.client.authenticated:
			serverid = utils.HashServerId(
				packet.data['server_id'], 
				self.client.SharedSecret, 
				pubkey
			)
			print('Attempting to authenticate session with session.minecraft.net')
			rep = utils.AuthenticateMinecraftSession(
				self.client.username, 
				self.client.sessionid, 
				serverid
			)
			if rep != 'OK':
				print('Session Authentication Failed, Response:', rep)
				self.client.auth_err = True
				return
			print(rep)

		rsa_cipher = PKCS1_v1_5.new(RSA.importKey(pubkey))
		self.client.push(mcpacket.Packet(ident = 0xFC, data = {
			'shared_secret': rsa_cipher.encrypt(self.client.SharedSecret),
			'verify_token': rsa_cipher.encrypt(packet.data['verify_token']),
		}))