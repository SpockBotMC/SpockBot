from Crypto.Cipher import PKCS1_v1_5
from Crypto.PublicKey import RSA
from Crypto import Random
from spock import utils
from spock.mcp import mcdata, mcpacket, yggdrasil
from spock.plugins.plutils import pl_announce

class MCAuth:
	def __init__(self, client):
		self.client = client
		self.username = None
		self.shared_secret = None
		self.auth = yggdrasil.YggAuth()

	def start_session(self, username, password = ''):
		if self.client.authenticated:
			print("Attempting login with username:", username, "and password:", password)
			rep = self.auth.authenticate(username, password)
			if 'error' not in rep:
				print(rep)
			else:
				print('Login Unsuccessful, Response:', rep)
				self.client.auth_err = True
				if self.client.sess_quit:
					print("Authentication error, stopping...")
					self.client.kill = True
				return rep

			self.username = rep['selectedProfile']['name']
			self.sessionid = ':'.join((
				'token', 
				rep['accessToken'], 
				rep['selectedProfile']['id']
			))
		else:
			self.username = username

		return rep

	def gen_shared_secret(self):
		self.shared_secret = Random._UserFriendlyRNG.get_random_bytes(16)
		return self.shared_secret


@pl_announce('Auth')
class AuthPlugin:
	def __init__(self, ploader, settings):
		self.net = ploader.requires('Net')
		self.client = ploader.requires('Client')
		self.auth = MCAuth(self.client)
		self.auth.gen_shared_secret()
		ploader.reg_event_handler(0xFD, self.handleFD)
		ploader.reg_event_handler(0xFC, self.handleFC)
		ploader.provides('Auth', self.auth)

	#Encryption Key Response - Signals encryption was successful, ready to spawn
	def handleFC(self, name, packet):
		if packet.direction == mcdata.SERVER_TO_CLIENT:
			self.net.enable_crypto(self.auth.shared_secret)
			self.net.push(mcpacket.Packet(ident = 0xCD, data = {
				'payload': 0,
			}))

	#Encryption Key Request - Request for client to start encryption
	def handleFD(self, name, packet):
		pubkey = packet.data['public_key']
		if self.client.authenticated:
			serverid = utils.HashServerId(
				packet.data['server_id'], 
				self.auth.shared_secret, 
				pubkey
			)
			print('Attempting to authenticate session with session.minecraft.net')
			rep = utils.AuthenticateMinecraftSession(
				self.auth.username, 
				self.auth.sessionid, 
				serverid
			)
			if rep != 'OK':
				print('Session Authentication Failed, Response:', rep)
				self.client.auth_err = True
				return
			print(rep)

		rsa_cipher = PKCS1_v1_5.new(RSA.importKey(pubkey))
		self.net.push(mcpacket.Packet(ident = 0xFC, data = {
			'shared_secret': rsa_cipher.encrypt(self.auth.shared_secret),
			'verify_token': rsa_cipher.encrypt(packet.data['verify_token']),
		}))