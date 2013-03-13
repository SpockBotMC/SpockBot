import select
import socket
import signal
import sys
import os
import logging

from Crypto import Random

import cipher
from spock.net.cflags import cflags
from spock.net.flag_handlers import fhandles
from spock.net.packet_handlers import phandles
from spock.net import timer
from spock.mcp import mcdata, mcpacket
from spock import utils, smpmap, bound_buffer

rmask = select.POLLIN|select.POLLERR|select.POLLHUP
smask = select.POLLOUT|select.POLLIN|select.POLLERR|select.POLLHUP

class Client(object):
	def __init__(self, **kwargs):
		#Grab some settings
		self.daemon = kwargs.get('daemon', False)
		self.logfile = kwargs.get('argfile', '')
		self.pidfile = kwargs.get('pidfile', '')
		plugins = kwargs.get('plugins', [])
		self.authenticated = kwargs.get('authenticated', True)
		self.bufsize = kwargs.get('bufsize', 4096)
		self.timeout = kwargs.get('timeout', 1)
		self.proxy = kwargs.get('proxy', {
			'enabled': False,
			'host': '',
			'port': 0,
			}
		)

		#Initialize plugin list
		#Plugins should never touch this
		self.timers = []
		self.plugin_handlers = {flag: [] for name, flag in cflags.iteritems()}
		self.plugin_dispatch = {ident: [] for ident in mcdata.structs}
		self.plugins = [plugin(self) for plugin in plugins]

		#Initialize socket and poll
		#Plugins should never touch these unless they know what they're doing
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.setblocking(0)
		self.poll = select.poll()
		self.poll.register(self.sock, smask)

		#Initialize Event Loop/Network variables
		#Plugins should generally not touch these
		self.encrypted = False
		self.kill = False
		self.auth_err = False
		self.login_err = False
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

	#Convenience method for starting a client
	def start(self, username, password = '', host = 'localhost', port = 25565):
		if self.daemon: self.start_daemon()
		self.start_session(username, password)
		self.login(host, port)
		self.event_loop()
		self.exit()

	def event_loop(self):
		#Set up signal handlers
		signal.signal(signal.SIGINT, self.signal_handler)
		signal.signal(signal.SIGTERM, self.signal_handler)
		#Fire off plugins that need to run after init
		for callback in self.plugin_handlers[cflags['START_EVENT']]: callback(flag)

		while not (self.flags&cflags['KILL_EVENT'] and self.kill):
			self.getflags()
			if self.flags:
				for name, flag in cflags.iteritems():
					if self.flags&flag:
						#Default handlers
						if flag in fhandles: fhandles[flag](self)
						#Plugin handlers
						for callback in self.plugin_handlers[flag]: callback(flag)
			for index, timer in enumerate(self.timers):
				if timer.update():
					timer.fire()
				if not timer.check():
					del self.timers[index]
			if self.daemon:
				sys.stdout.flush()
				sys.stderr.flush()

	def getflags(self):
		self.flags = 0
		if self.sbuff:
			self.poll.register(self.sock, smask)
		else:
			self.poll.register(self.sock, rmask)
		try:
			poll = self.poll.poll(self.timeout)
		except select.error, e:
			logging.error(str(e))
			poll = []
		if poll:
			poll = poll[0][1]
			if poll&select.POLLERR:                self.flags += cflags['SOCKET_ERR']
			if poll&select.POLLHUP:                self.flags += cflags['SOCKET_HUP']
			if poll&select.POLLOUT and self.sbuff: self.flags += cflags['SOCKET_SEND']
			if poll&select.POLLIN:                 self.flags += cflags['SOCKET_RECV']
		if self.rbuff:                         self.flags += cflags['RBUFF_RECV']
		if self.login_err:                     self.flags += cflags['LOGIN_ERR']; self.login_err = False
		if self.auth_err:                      self.flags += cflags['AUTH_ERR']; self.auth_err = False
		if self.kill:                          self.flags += cflags['KILL_EVENT']

	def dispatch_packet(self, packet):
		#Default dispatch
		if packet.ident in phandles:
			phandles[packet.ident].handle(self, packet.clone())
		#Plugin dispatchers
		for callback in self.plugin_dispatch[packet.ident]:
			callback(packet.clone())

	def register_dispatch(self, callback, *idents):
		for ident in idents:
			self.plugin_dispatch[ident].append(callback)

	def register_handler(self, callback, *flags):
		for flag in flags:
			self.plugin_handlers[flag].append(callback)

	def register_timer(self, timer):
		self.timers.append(timer)

	def connect(self, host = 'localhost', port=25565):
		if self.proxy['enabled']:
			self.host = self.proxy['host']
			self.port = self.proxy['port']
		else:
			self.host = host
			self.port = port
		try:
			print "Attempting to connect to host:", self.host, "port:", self.port
			self.sock.connect((self.host, self.port))
		except socket.error as error:
			logging.info("Error on Connect (this is normal): " + str(error))

	def exit(self):
		self.push(mcpacket.Packet(ident = 0xFF, data = {
			'reason': 'KILL_EVENT recieved'
			})
		)
		while self.sbuff:
			self.getflags()
			if self.flags&(cflags['SOCKET_ERR']|cflags['SOCKET_HUP']):
				break
			elif self.flags&cflags['SOCKET_SEND']:
				fhandles[cflags['SOCKET_SEND']](self)
		self.sock.close()

		if self.pidfile and os.path.exists(self.pidfile):
			os.remove(self.pidfile)

		sys.exit(0)


	def enable_crypto(self, SharedSecret):
		self.cipher = cipher.AESCipher(SharedSecret)
		self.encrypted = True

	def push(self, packet):
		bytes = packet.encode()
		self.sbuff += (self.cipher.encrypt(bytes) if self.encrypted else bytes)
		self.dispatch_packet(packet)

	def login(self, host = 'localhost', port = 25565):
		self.connect(host, port)
		self.SharedSecret = Random._UserFriendlyRNG.get_random_bytes(16)

		#Stage 2: Send initial handshake
		self.push(mcpacket.Packet(ident = 02, data = {
			'protocol_version': mcdata.MC_PROTOCOL_VERSION,
			'username': self.username,
			'host': host,
			'port': port,
			})
		)

	def start_session(self, username, password = ''):
		self.mc_username = username
		self.mc_password = password

		#Stage 1: Login to Minecraft.net
		if self.authenticated:
			print "Attempting login with username:", username, "and password:", password
			LoginResponse = utils.LoginToMinecraftNet(username, password)
			print LoginResponse
			if (LoginResponse['Response'] != "Good to go!"):
				logging.error('Login Unsuccessful, Response: %s', LoginResponse['Response'])
				self.login_err = True
				return LoginResponse

			self.username = LoginResponse['Username']
			self.sessionid = LoginResponse['SessionID']
		else:
			self.username = username

	def start_daemon(self, daemonize = False):
		self.daemon = True
		if daemonize:
			utils.daemonize()
			Random.atfork()

		self.pid = os.getpid()
		if self.logfile:
			sys.stdout = sys.stderr = open(self.logfile, 'w')
		if self.pidfile:
			pidf = open(self.pidfile, 'w')
			pidf.write(str(self.pid))
			pidf.close()

	def enable_proxy(self, host, port):
		self.proxy['enabled'] = True
		self.proxy['host'] = host
		self.proxy['port'] = port

	def signal_handler(self, *args):
		self.kill = True