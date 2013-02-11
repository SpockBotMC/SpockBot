import select
import socket
import logging

from Crypto.Random import _UserFriendlyRNG

import cipher
from spock.net.cflags import cflags
from spock.net.flag_handlers import fhandles
from spock.net.packet_handlers import phandles
from spock.mcp import mcdata, mcpacket
from spock import utils, smpmap, bound_buffer

class Client:
	def __init__(self, plugins = []):
		#Initialize plugin list
		#Plugins should never touch this
		self.plugin_handlers = []
		self.plugin_dispatch = {ident: [] for ident in mcdata.structs}
		self.plugins = [plugin(self) for plugin in plugins]

		#Initialize socket and poll
		#Plugins should never touch these unless they know what they're doing
		self.bufsize = 4096
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.setblocking(0)
		self.poll = select.poll()
		self.poll.register(self.sock)

		#Initialize Event Loop/Network variables
		#Plugins should generally not touch these
		self.encrypted = False
		self.kill = False
		self.rbuff = bound_buffer.BoundBuffer()
		self.sbuff = ''
		self.flags = 0 #OK to read flags, not write

		#State variables
		#Plugins should read these (but generally not write)
		self.world = smpmap.World()
		self.world_time = {
			'world_age': 0,
			'time_of_day': 0,
		}
		self.position = {
			'x': 0,
			'y': 0,
			'z': 0,
			'stance': 0,
			'yaw': 0,
			'pitch': 0,
			'on_ground': False,
		}
		self.health = {
			'health': 20,
			'food': 20,
			'food_saturation': 5,
		}
		self.playerlist = {}
		self.entitylist = {}
		self.spawn_position = {
			'x': 0,
			'y': 0,
			'z': 0,
		}
		self.login_info = {}

	#Convenience method for logging into authenticated servers
	def start(self, username, password, host = 'localhost', port=25565):
		self.start_session(username, password)
		self.login(host, port)
		self.event_loop()

	def event_loop(self):
		while not self.kill:
			#Poll
			self.getflags()
			#Default handlers
			for name, flag in cflags.iteritems():
				if self.flags&flag: fhandles[flag](self)
			#Plugin handlers
			for callback in self.plugin_handlers:
				callback()

	def getflags(self):
		self.flags = 0
		poll = self.poll.poll()[0][1]
		if poll&select.POLLOUT and self.sbuff: self.flags += cflags['SOCKET_SEND']
		if poll&select.POLLIN:                 self.flags += cflags['SOCKET_RECV']
		if self.rbuff:                         self.flags += cflags['RBUFF_RECV']

	def dispatch_packet(self, packet):
		#Default dispatch
		if packet.ident in phandles:
			phandles[packet.ident].handle(self, packet)
		#Plugin dispatchers
		for callback in self.plugin_dispatch[packet.ident]:
			callback(packet)

	def register_dispatch(self, callback, ident):
		self.plugin_dispatch[ident].append(callback)

	def register_handler(self, callback):
		self.plugin_handlers.append(callback)

	def connect(self, host = 'localhost', port=25565):
		self.host = host
		self.port = port
		try:
			self.sock.connect((host, port))
		except socket.error as error:
			logging.info("Error on Connect (this is normal): " + str(error))

	def enable_crypto(self, SharedSecret):
		self.cipher = cipher.AESCipher(SharedSecret)
		self.encrypted = True

	def push(self, packet):
		bytes = packet.encode()
		self.sbuff += (self.cipher.encrypt(bytes) if self.encrypted else bytes)
		self.dispatch_packet(packet)

	def login(self, host = 'localhost', port=25565):
		self.connect(host, port)
		self.SharedSecret = _UserFriendlyRNG.get_random_bytes(16)

		#Stage 2: Send initial handshake
		self.push(mcpacket.Packet(ident = 02, data = {
				'protocol_version': mcdata.MC_PROTOCOL_VERSION,
				'username': self.username,
				'host': host,
				'port': port,
				})
			)

	def start_session(self, username, password):
		#Stage 1: Login to Minecraft.net
		LoginResponse = utils.LoginToMinecraftNet(username, password)
		if (LoginResponse['Response'] != "Good to go!"):
			logging.error('Login Unsuccessful, Response: %s', LoginResponse['Response'])
			return LoginResponse['Response']

		self.username = LoginResponse['Username']
		self.sessionid = LoginResponse['SessionID']