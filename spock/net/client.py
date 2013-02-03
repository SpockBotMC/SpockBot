import select
import socket
import logging

from Crypto.Random import _UserFriendlyRNG
from Crypto.Util import asn1
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES
from Crypto.Cipher import PKCS1_v1_5

import smpmap
from spock.mcp.packet import Packet, decode_packet
from spock.mcp import utils, mcdata


bufsize = 4096

class Client:
	def __init__(self):
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.setblocking(0)
		self.poll = select.poll()
		self.poll.register(self.sock)

		self.world = smpmap.World()
		self.encrypted = False
		self.sbuff = ''

	def connect(self, host = 'localhost', port=25565):
		self.host = host
		self.port = port
		try:
			self.sock.connect((host, port))
		except socket.error as error:
			logging.info("Error on Connect (this is normal): " + str(error))

	def enable_crypto(self, SharedSecret):
		self.encipher = AES.new(SharedSecret, AES.MODE_CFB, IV=SharedSecret)
		self.decipher = AES.new(SharedSecret, AES.MODE_CFB, IV=SharedSecret)
		self.encrypted = True

	def push(self, packet):
		self.sbuff+=packet.encode()

	def run(self, plugins):
		pass

	def login(self, username, password, host = 'localhost', port=25565):
		#Stage 0: Login to Minecraft.net
		LoginResponse = utils.LoginToMinecraftNet(username, password)
		if (LoginResponse['Response'] != "Good to go!"):
			logging.error('Login Unsuccessful, Response: %s', LoginResponse['Response'])
			return

		#Stage 1: Send initial handshake
		self.username = LoginResponse['Username']
		self.sessionid = LoginResponse['SessionID']
		self.connect(host, port)
		while not self.poll.poll()[0][1]&select.POLLOUT:
			pass
		self.sock.send(Packet(ident = 02, data = {
				'protocol_version': mcdata.MC_PROTOCOL_VERSION,
				'username': self.username,
				'host': host,
				'port': port,
				}).encode()
			)
		while not self.poll.poll()[0][1]&select.POLLIN:
			pass
		packet = decode_packet(self.sock.recv(bufsize))
		if (packet.ident != 0xFD):
			logging.error('Server responded with incorrect packet after handshake: %s', str(hex(packet.ident)))
			return

		#Stage 2: Authenticate with session.minecraft.net
		pubkey = packet.data['public_key']
		SharedSecret = _UserFriendlyRNG.get_random_bytes(16)
		serverid = utils.HashServerId(packet.data['server_id'], SharedSecret, pubkey)
		SessionResponse = utils.AuthenticateMinecraftSession(self.username, self.sessionid, serverid)
		if (SessionResponse != 'OK'):
			logging.error('Session Authentication Failed, Response: %s', SessionResponse)
			return

		#Stage 3: Send an Encryption Response
		RSACipher = PKCS1_v1_5.new(RSA.importKey(pubkey))
		encryptedSanityToken = RSACipher.encrypt(str(packet.data['verify_token']))
		encryptedSharedSecret = RSACipher.encrypt(str(SharedSecret))
		while not self.poll.poll()[0][1]&select.POLLOUT:
			pass
		self.sock.send(Packet(ident = 0xFC, data = {
			'shared_secret': encryptedSharedSecret,
			'verify_token': encryptedSanityToken,
			}).encode()
		)
		while not self.poll.poll()[0][1]&select.POLLIN:
			pass
		packet = decode_packet(self.sock.recv(bufsize))
		if (packet.ident != 0xFC):
			logging.error('Server responded with incorrect packet after encryption response: %s', str(hex(packet.ident)))
			return

		#Stage 4: Enable encryption and send Client Status
		self.enable_crypto(SharedSecret)
		while not self.poll.poll()[0][1]&select.POLLOUT:
			pass
		self.sock.send(self.encipher.encrypt(Packet(ident = 0xCD, data = {
			'payload': 0,
			}).encode())
		)
		while not self.poll.poll()[0][1]&select.POLLIN:
			pass
		packet = decode_packet(self.decipher.decrypt(self.sock.recv(bufsize)))
		if (packet.ident != 0x01):
			logging.error('Server responded with incorrect packet after client status: %s', str(hex(packet.ident)))
			return