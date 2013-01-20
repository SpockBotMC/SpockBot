import select
import socket
import logging

from Crypto.Random import _UserFriendlyRNG
from Crypto.Util import asn1
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES
from Crypto.Cipher import PKCS1_v1_5

from spock.mcp.packet import Packet, decode_packet
from spock.mcp import utils, mcdata

bufsize = 4096

class Client:
	def __init__(self):
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.socket.setblocking(0)
		self.poll = select.poll()
		self.poll.register(self.socket)

		self.encrypted = False
		self.sbuff = ''

	def connect(self, host = 'localhost', port=25565):
		self.host = host
		self.port = port
		try:
			self.socket.connect((host, port))
		except socket.error as error:
			logging.info("Error on Connect (this is normal): " + str(error))

	def enable_crypto(self, cipher):
		self.cipher = cipher
		self.encrypted = True

	def login(self, username, password):
		LoginResponse = utils.LoginToMinecraftNet(username, password)
		if (LoginResponse['Response'] != "Good to go!"):
			logging.error('Login Unsuccessful, Response: %s', LoginResponse['Response'])
			return
		self.username = LoginResponse['Username']
		self.sessionid = LoginResponse['SessionID']
		self.connect('192.168.1.108')
		buff = Packet(ident = 02, data = {
			'protocol_version': mcdata.MC_PROTOCOL_VERSION,
			'username': username,
			'server_host': self.host,
			'server_port': self.port,
			}).encode()
		while buff:
			while not self.poll.poll()[0][1]&select.POLLOUT:
				pass
			sent = self.socket.send(buff)
			buff = buff[sent:]
		data = self.poll.poll()
		print data
		while not data[0][1]&select.POLLIN:
			data = self.poll.poll()
			print data
		packet = decode_packet(self.socket.recv(bufsize))
		if (packet.ident != 0xFD):
			logging.error('Server responded with incorrect packet after handshake: %s', str(packet.ident))
			return

		#Stage 2: Authenticate with session.minecraft.net
		pubkey = packet.data['public_key']
		self.SharedSecret = _UserFriendlyRNG.get_random_bytes(16)
		serverid = utils.HashServerId(packet.data['server_id'], self.SharedSecret, pubkey)
		SessionResponse = utils.AuthenticateMinecraftSession(self.username, self.sessionid, serverid)
		if (SessionResponse != 'OK'):
			logging.error('Session Authentication Failed, Response: %s', SessionResponse)
			return

		#Stage 3: Send an Encryption Response
		RSACipher = PKCS1_v1_5.new(RSA.importKey(pubkey))
		encryptedSanityToken = RSACipher.encrypt(str(packet.data['verify_token']))
		encryptedSharedSecret = RSACipher.encrypt(str(self.SharedSecret))
		while not self.poll.poll()[0][1]&select.POLLOUT:
			pass
		self.socket.send(Packet(ident = 0xFC, data = {
			'shared_secret_length': encryptedSharedSecret.__len__(),
			'shared_secret': encryptedSharedSecret,
			'verify_token_length': encryptedSanityToken.__len__(),
			'verify_token': encryptedSanityToken,
			}).encode()
		)
		while not self.poll.poll()[0][1]&select.POLLIN:
			pass
		packet = decode_packet(self.socket.recv(bufsize))
		if (packet.ident != 0xFC):
			logging.error('Server responded with incorrect packet after encryption response: %s', str(packet.ident))
			return

		#Stage 4: Enable encryption and send Client Status
		self.enable_crypto(AES.new(self.SharedSecret, AES.MODE_CFB, IV=self.SharedSecret))
		while not self.poll.poll()[0][1]&select.POLLOUT:
			pass
		self.socket.send(self.cipher.encrypt(Packet(ident = 0xCD, data = {
			'payload': 0,
			}).encode())
		)
		while not self.poll.poll()[0][1]&select.POLLIN:
			pass
		packet = decode_packet(self.cipher.decrypt(self.socket.recv(bufsize)))
		if (packet.ident != 0x01):
			logging.error('Server responded with incorrect packet after client status: %s', str(packet.ident))
			return
