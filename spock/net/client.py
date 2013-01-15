import logging
import urllib2
import mcsocket
import packet_queue


from Crypto.Random import _UserFriendlyRNG
from Crypto.Util import asn1
from Crypto.Cipher import AES
from Crypto.Cipher import PKCS1_v1_5
from Crypto.PublicKey import RSA

from spock.mcp import bound_buffer, utils, mcdata
from spock.mcp.packet import Packet, read_packet 

from encrypt import HashServerId


#For authenticating servers only
class Client:
	def __init__(self, **custom_settings):
		self.rbuff = bound_buffer.BoundBuffer()
		self.pqueue = packet_queue.PacketQueue()
		self.socket = mcsocket.CryptoAsyncSocket(self.rbuff, self.pqueue)

	#This function is way too complex and handles way too much
	#TODO: Split this up to allow for indepent login and authentication
	#TODO: Consider possibility of exporting login to plugin (Should be trivial, ya?)
	def login(self, host, port, username, password):
		LoginResponse = utils.LoginToMinecraftNet(username, password)
		if (LoginResponse['Response'] != "Good to go!"):
			logging.error('Login Unsuccessful, Response: %s', LoginResponse['Response'])
			return	
		username = LoginResponse['Username']
		sessionid = LoginResponse['SessionID']
		#TODO: Ugly as hell, refactor this whole data flow
		self.socket.sbuff.append(Packet(ident = 02, data = {
			'protocol_version': mcdata.MC_PROTOCOL_VERSION,
			'username': username,
			'server_host': host,
			'server_port': port,
			}).encode()
		)

		packet = None
		while not packet:
			packet = self.get_packet()
		if (packet.ident != 0xFD):
			logging.error('Server responded with incorrect packet after handshake: %s', str(packet.ident))
			return
		pubkey = packet.data['public_key']
		self.SharedSecret = _UserFriendlyRNG.get_random_bytes(16)
		serverid = HashServerId(packet.data['server_id'], self.SharedSecret, pubkey)
		url = "http://session.minecraft.net/game/joinserver.jsp?user=" + username + "&sessionId=" + sessionid + "&serverId=" + serverid
		SessionResponse = urllib2.urlopen(url).read()
		if (SessionResponse != 'OK'):
			logging.error('Session Authentication Failed, Response: %s', SessionResponse)
			return

		RSACipher = PKCS1_v1_5.new(RSA.importKey(pubkey))
		encryptedSanityToken = RSACipher.encrypt(str(packet.data['verify_token']))
		encryptedSharedSecret = RSACipher.encrypt(str(sharedSecret))
		self.socket.sbuff.append(Packet(ident = 0xFC, data = {
			'shared_secret_length': encryptedSharedSecret.__len__(),
			'shared_secret': encryptedSharedSecret,
			'verify_token_length': encryptedSanityToken.__len__(),
			'verify_token': encryptedSanityToken,
			}).encode()
		)
		packet = None
		while not packet:
			packet = self.get_packet()
		if (packet.ident != 0xFC):
			logging.error('Server responded with incorrect packet after encryption response: %s', str(packet.ident))
			return

		self.socket.cipher = AES.new(self.SharedSecret, AES.MODE_CFB, IV=self.SharedSecret)
		self.socket.enable_crypto()
		self.socket.sbuff.append(Packet(ident = 0xCD, data = {
			'payload': 0,
			}).encode()
		)
		packet = None
		while not packet:
			packet = self.get_packet()
		if (packet.ident != 0x01):
			logging.error('Server responded with incorrect packet after client status: %s', str(packet.ident))
			return


	def get_packet(self):
		while self.rbuff.buff:
			try:
				packet = read_packet(self.rbuff)
				self.rbuff.save()
			except bound_buffer.BufferUnderflowException:
				self.rbuff.revert()
				return
		return packet
