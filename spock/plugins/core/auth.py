"""
Provides authorization functions for Mojang's login and session servers
"""

import hashlib
import urllib.request as request
import json
from urllib.error import URLError
from Crypto.Cipher import PKCS1_v1_5
from Crypto.PublicKey import RSA
from Crypto import Random
from spock import utils
from spock.mcp import mcdata, mcpacket, yggdrasil
from spock.utils import pl_announce

# This function courtesy of barneygale
def JavaHexDigest(digest):
	d = int(digest.hexdigest(), 16)
	if d >> 39 * 4 & 0x8:
		d = "-%x" % ((-d) & (2 ** (40 * 4) - 1))
	else:
		d = "%x" % d
	return d

class AuthCore:
	def __init__(self, authenticated, event):
		self.event = event
		self.authenticated = authenticated
		self.username = None
		self.selected_profile = None
		self.shared_secret = None
		self.ygg = yggdrasil.YggAuth()

	def start_session(self, username, password = ''):
		rep = {}
		if self.authenticated:
			print(
				"Attempting login with username:", username,
				"and password:", password
			)
			rep = self.ygg.authenticate(username, password)
			if rep != None and 'error' not in rep:
				print(rep)
			else:
				print('Login Unsuccessful, Response:', rep)
				self.event.emit('AUTH_ERR')
				return rep
			if 'selectedProfile' in rep:
				self.selected_profile = rep['selectedProfile']
				self.username = rep['selectedProfile']['name']
			else:
				self.username = username
		else:
			self.username = username
		return rep

	def gen_shared_secret(self):
		self.shared_secret = Random._UserFriendlyRNG.get_random_bytes(16)
		return self.shared_secret


@pl_announce('Auth')
class AuthPlugin:
	def __init__(self, ploader, settings):
		self.event = ploader.requires('Event')
		self.net = ploader.requires('Net')
		settings = ploader.requires('Settings')
		self.authenticated = settings['authenticated']
		self.sess_quit = settings['sess_quit']
		self.auth = AuthCore(self.authenticated, self.event)
		self.auth.gen_shared_secret()
		ploader.reg_event_handler('AUTH_ERR', self.handleAUTHERR)
		ploader.reg_event_handler('SESS_ERR', self.handleSESSERR)
		ploader.reg_event_handler(
			(mcdata.LOGIN_STATE, mcdata.SERVER_TO_CLIENT, 0x01),
			self.handle01
		)
		ploader.provides('Auth', self.auth)

	def handleAUTHERR(self, name, data):
		self.event.kill()

	def handleSESSERR(self, name, data):
		if self.sess_quit:
			self.event.kill()

	#Encryption Key Request - Request for client to start encryption
	def handle01(self, name, packet):
		pubkey = packet.data['public_key']
		if self.authenticated:
			serverid = JavaHexDigest(hashlib.sha1(
				packet.data['server_id'].encode('ascii')
				+ self.auth.shared_secret
				+ pubkey
			))
			print('Attempting to authenticate session with sessionserver.mojang.com')
			url = "https://sessionserver.mojang.com/session/minecraft/join"
			data = json.dumps({
				'accessToken': self.auth.ygg.access_token,
				'selectedProfile': self.auth.selected_profile,
				'serverId': serverid,
			}).encode('utf-8')
			headers = {'Content-Type': 'application/json'}
			req = request.Request(url, data, headers, method='POST')
			try:
				rep = request.urlopen(req).read().decode('ascii')
			except URLError:
				rep = 'Couldn\'t connect to sessionserver.mojang.com'
			#if rep != 'OK':
			#	print('Session Authentication Failed, Response:', rep)
			#	self.event.emit('SESS_ERR')
			#	return
			print(rep)

		rsa_cipher = PKCS1_v1_5.new(RSA.importKey(pubkey))
		self.net.push(mcpacket.Packet(
			ident = (mcdata.LOGIN_STATE, mcdata.CLIENT_TO_SERVER, 0x01),
			data = {
				'shared_secret': rsa_cipher.encrypt(self.auth.shared_secret),
				'verify_token': rsa_cipher.encrypt(packet.data['verify_token']),
			}
		))
		self.net.enable_crypto(self.auth.shared_secret)
