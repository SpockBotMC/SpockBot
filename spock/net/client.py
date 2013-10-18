import select
import socket
import signal
import sys

from Crypto import Random

from spock.net.extensions.pluginloader import PluginLoader
from spock.net.auth.yggdrasil import YggAuth
from spock.net.eventhandlers import ClientEventHandlers
from spock.net.event import Event
from spock.net import timer, cipher, cflags
from spock.mcp import mcdata, mcpacket
from spock import utils, smpmap, bound_buffer

rmask = select.POLLIN|select.POLLERR|select.POLLHUP
smask = select.POLLOUT|select.POLLIN|select.POLLERR|select.POLLHUP

class Client(object):
	def __init__(self, **kwargs):
		#Grab some settings
		self.settings = cflags.SettingsDummy()
		settings = kwargs.get('settings', {})
		for setting in cflags.defstruct:
			val = kwargs.get(setting[1], settings.get(setting[1], setting[2]))
			setattr(self, setting[0], val)

		#Initialize plugin list
		#Plugins should never touch this
		self.timers = []
		self.event_handlers = {ident: [] for ident in mcdata.structs}
		self.event_handlers.update({event: [] for event in cflags.cevents})
		self.event_handlers.update({event: [] for event in cflags.cflags})
		self.plugins.insert(0, ClientEventHandlers)
		PluginLoader(self, self.plugins)

		#Initialize socket and poll
		#Plugins should never touch these unless they know what they're doing
		self.auth = YggAuth()
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.setblocking(0)
		self.poll = select.poll()
		self.poll.register(self.sock, smask)

		#Initialize Event Loop/Network variables
		#Plugins should generally not touch these
		self.encrypted = False
		self.kill = False
		self.auth_err = False
		self.sess_err = False
		self.rbuff = bound_buffer.BoundBuffer()
		self.sbuff = b''

		#Game State variables
		#Plugins should read these (but generally not write)
		self.world = smpmap.World()
		self.world_time = {
			'world_age': 0,
			'time_of_day': 0,
		}
		self.entitylist = {}

	#Convenience method for starting a client
	def start(self, host = 'localhost', port = 25565):
		if 'error' not in self.start_session(self.mc_username, self.mc_password):
			self.connect(host, port)
			self.handshake()
			self.event_loop()
		self.exit()

	def event_loop(self):
		#Set up signal handlers
		signal.signal(signal.SIGINT, self.signal_handler)
		signal.signal(signal.SIGTERM, self.signal_handler)
		#Fire off plugins that need to run after init
		self.emit('start')

		while not self.kill:
			flags = self.get_flags()
			for flag in flags:
				self.emit(flag)
			for index, timer in enumerate(self.timers):
				if timer.update():
					timer.fire()
				if not timer.check():
					del self.timers[index]

	def get_flags(self):
		flags = []
		if self.sbuff:
			self.poll.register(self.sock, smask)
		else:
			self.poll.register(self.sock, rmask)
		try:
			poll = self.poll.poll(self.get_timeout())
		except select.error as e:
			print(str(e))
			poll = []
		if poll:
			poll = poll[0][1]
			if poll&select.POLLERR: flags.append('SOCKET_ERR')
			if poll&select.POLLHUP: flags.append('SOCKET_HUP')
			if poll&select.POLLOUT: flags.append('SOCKET_SEND')
			if poll&select.POLLIN:  flags.append('SOCKET_RECV')
		if self.auth_err:           flags.append('AUTH_ERR'); self.auth_err = False
		if self.sess_err:           flags.append('SESS_ERR'); self.sess_err = False
		return flags

	def get_timeout(self):
		timeout = -1
		for timer in self.timers:
			if timeout > timer.countdown() or timout == -1:
					timeout = timer.countdown()

		return timeout

	def emit(self, name, data=None):
		event = (data if name in mcdata.structs else Event(name, data))
		for handler in self.event_handlers[name]:
			handler(name, data)

	def reg_event_handler(self, events, handlers):
		if isinstance(events, str) or not hasattr(events, '__iter__'): 
			events = [events]
		if not hasattr(handlers, '__iter__'):
			handlers = [handlers]

		for event in events:
			self.event_handlers[event].extend(handlers)

	def register_timer(self, timer):
		self.timers.append(timer)

	def connect(self, host = 'localhost', port = 25565):
		if self.proxy['enabled']:
			self.host = self.proxy['host']
			self.port = self.proxy['port']
		else:
			self.host = host
			self.port = port
		try:
			print("Attempting to connect to host:", self.host, "port:", self.port)
			self.sock.connect((self.host, self.port))
		except socket.error as error:
			#print("Error on Connect (this is normal):", str(error))
			pass

	def kill(self):
		self.emit('kill')
		self.kill = True

	def exit(self):
		flags = self.get_flags()
		if not 'SOCKET_HUP' in flags:
			self.push(mcpacket.Packet(ident = 0xFF, data = {
				'reason': 'disconnect.quitting'
				})
			)
			while self.sbuff:
				flags = self.get_flags()
				if ('SOCKET_ERR' in flags) or ('SOCKET_HUP' in flags):
					break
				elif 'SOCKET_SEND' in flags:
					self.emit('SOCKET_SEND')
			self.sock.close()

		sys.exit(0)

	def enable_crypto(self, SharedSecret):
		self.cipher = cipher.AESCipher(SharedSecret)
		self.encrypted = True

	def push(self, packet):
		bytes = packet.encode()
		self.sbuff += (self.cipher.encrypt(bytes) if self.encrypted else bytes)
		self.emit(packet.ident, packet)

	def start_session(self, username, password = ''):
		self.mc_username = username
		self.mc_password = password

		#Stage 1: Login to Minecraft.net
		if self.authenticated:
			print("Attempting login with username:", username, "and password:", password)
			rep = self.auth.authenticate(username, password)
			if 'error' not in rep:
				print(rep)
			else:
				print('Login Unsuccessful, Response:', rep)
				self.auth_err = True
				if self.sess_quit:
					print("Authentication error, stopping...")
					self.kill = True
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

	def reset(self):
		self.poll.unregister(self.sock)
		self.sock.close()
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.setblocking(0)
		self.poll.register(self.sock)
	
		self.sbuff = b''
		self.rbuff.flush()
		self.encrypted = False
		self.world = smpmap.World()
		self.world_time = {
			'world_age': 0,
			'time_of_day': 0,
		}
		self.playerlist = {}
		self.entitylist = {}

	def handshake(self):
		self.SharedSecret = Random._UserFriendlyRNG.get_random_bytes(16)

		#Stage 2: Send initial handshake
		self.push(mcpacket.Packet(ident = 0x02, data = {
			'protocol_version': mcdata.MC_PROTOCOL_VERSION,
			'username': self.username,
			'host': self.host,
			'port': self.port,
			})
		)

	def enable_proxy(self, host, port):
		self.proxy['enabled'] = True
		self.proxy['host'] = host
		self.proxy['port'] = port

	def signal_handler(self, *args):
		self.kill = True
