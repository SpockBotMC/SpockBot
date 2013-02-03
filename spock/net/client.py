import select
import socket
import logging

from Crypto.Random import _UserFriendlyRNG
from Crypto.Cipher import AES

from spock.net.client_flags import cflags
from spock.net.flag_handlers import fhandles
from spock.net.packet_handlers import phandles
from spock.mcp import mcdata, mcpacket
from spock import utils, smpmap, bound_buffer



class Client:
	def __init__(self):
		self.bufsize = 4096

		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.setblocking(0)
		self.poll = select.poll()
		self.poll.register(self.sock)

		self.world = smpmap.World()
		self.encrypted = False
		self.kill = False
		self.rbuff = bound_buffer.BoundBuffer()
		self.sbuff = ''

	def run(self):
		while not self.kill:
			flags = self.getflags()
			flags = self.update(flags)

	def update(self, flags):
		for name, flag in cflags.iteritems():
			if flags&flag: fhandles[flag](self)

	def getflags(self):
		flags = 0
		poll = self.poll.poll()[0][1]
		if poll&select.POLLOUT and self.sbuff: flags = flags|cflags['SOCKET_SEND']
		if poll&select.POLLIN:                 flags = flags|cflags['SOCKET_RECV']
		if self.rbuff:                         flags = flags|cflags['RBUFF_RECV']
		return flags

	def dispatch_packet(self, packet):
		if packet.ident in phandles:
			phandles[packet.ident].handle(self, packet)
		#print packet

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
		bytes = packet.encode()
		self.sbuff += (self.encipher.encrypt(bytes) if self.encrypted else bytes)

	def login(self, username, password, host = 'localhost', port=25565):
		#Stage 1: Login to Minecraft.net
		LoginResponse = utils.LoginToMinecraftNet(username, password)
		if (LoginResponse['Response'] != "Good to go!"):
			logging.error('Login Unsuccessful, Response: %s', LoginResponse['Response'])
			return

		self.username = LoginResponse['Username']
		self.sessionid = LoginResponse['SessionID']
		self.SharedSecret = _UserFriendlyRNG.get_random_bytes(16)
		self.connect(host, port)

		#Stage 2: Send initial handshake
		self.push(mcpacket.Packet(ident = 02, data = {
				'protocol_version': mcdata.MC_PROTOCOL_VERSION,
				'username': self.username,
				'host': host,
				'port': port,
				})
			)

		self.run()