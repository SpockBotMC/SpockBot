import hashlib
import urllib.request as request
import json
from urllib.error import URLError
from Crypto.Cipher import PKCS1_v1_5
from Crypto.PublicKey import RSA
from Crypto import Random
from spock import utils
from spock.mcp import mcdata, mcpacket, yggdrasil
from spock.plugins.plutils import pl_announce

# This function courtesy of barneygale
def JavaHexDigest(digest):
	d = int(digest.hexdigest(), 16)
	if d >> 39 * 4 & 0x8:
		d = "-%x" % ((-d) & (2 ** (40 * 4) - 1))
	else:
		d = "%x" % d
	return d

class MCAuth:
	def __init__(self, client):
		self.client = client
		self.username = None
		self.selected_profile = None
		self.shared_secret = None
		self.ygg = yggdrasil.YggAuth()

	def start_session(self, username, password = ''):
		if self.client.authenticated:
			print(
				"Attempting login with username:", username, 
				"and password:", password
			)
			rep = self.ygg.authenticate(username, password)
			if 'error' not in rep:
				print(rep)
			else:
				print('Login Unsuccessful, Response:', rep)
				self.client.auth_err = True
				if self.client.sess_quit:
					print("Authentication error, stopping...")
					self.client.kill = True
				return rep

			self.selected_profile = rep['selectedProfile']
			self.username = rep['selectedProfile']['name']
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
		ploader.reg_event_handler(
			(mcdata.LOGIN_STATE, mcdata.SERVER_TO_CLIENT, 0x01), 
			self.handle01
		)
		ploader.provides('Auth', self.auth)

	#Encryption Key Request - Request for client to start encryption
	def handle01(self, name, packet):
		pubkey = packet.data['public_key']
		if self.client.authenticated:
			serverid = JavaHexDigest(hashlib.sha1(
				packet.data['server_id'].encode('ascii')
				+ self.auth.shared_secret
				+ pubkey
			))
			print('Attempting to authenticate session with serversession.mojang.com')
			url = "https://sessionserver.mojang.com/session/minecraft/join"
			data = json.dumps({
				'accessToken': self.auth.ygg.access_token
				'selectedProfile': self.auth.selected_profile
				'serverId': serverid
			}).encode('utf-8')
			headers = {'Content-Type': 'application/json'}
			req = request.Request(url, data, headers, method='POST')
			try:
				rep = request.urlopen(req).read().decode('ascii')
			except URLError:
				rep = 'Couldn\'t connect to session.minecraft.net'
			#if rep != 'OK':
			#	print('Session Authentication Failed, Response:', rep)
			#	self.client.auth_err = True
			#	return
			print(rep)

		rsa_cipher = PKCS1_v1_5.new(RSA.importKey(pubkey))
		self.net.push(mcpacket.Packet(
			ident = (mcdata.CLIENT_TO_SERVER, mcdata.LOGIN_STATE, 0x01), 
			data = {
				'shared_secret': rsa_cipher.encrypt(self.auth.shared_secret),
				'verify_token': rsa_cipher.encrypt(packet.data['verify_token']),
			}
		))
		self.net.enable_crypto()