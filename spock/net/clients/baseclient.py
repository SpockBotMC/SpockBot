import select
import socket
import signal
import sys

from spock.net.pluginloader import PluginLoader
from spock.net import cflags
from spock.mcp import mcdata
from spock import utils

class BaseClient(object):
	def __init__(self, **kwargs):
		#Grab some settings
		self.settings = cflags.SettingsDummy()
		settings = kwargs.get('settings', {})
		for setting in cflags.defstruct:
			val = kwargs.get(setting[1], settings.get(setting[1], setting[2]))
			setattr(self, setting[0], val)

		#Initialize plugin list
		self.timers = []
		self.event_handlers = {}
		PluginLoader(self, self.plugins)

		#Initialize socket
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.setblocking(0)

		#Initialize Event Loop/Network variables
		self.send = False
		self.kill = False
		self.auth_err = False
		self.sess_err = False

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
		if self.send:
			self.send = False
			slist = [[self.sock], [self.sock], []]
		else:
			slist = [[self.sock], [], []]
		timeout = self.get_timeout()
		if timeout>0: 
			slist.append(timeout)
		try:
			rlist, wlist, xlist = select.select(*slist)
		except select.error as e:
			print(str(e))
			rlist = []
			wlist = []
		if rlist:         flags.append('SOCKET_RECV')
		if wlist:         flags.append('SOCKET_SEND')
		if self.auth_err: flags.append('AUTH_ERR'); self.auth_err = False
		if self.sess_err: flags.append('SESS_ERR'); self.sess_err = False
		return flags

	def get_timeout(self):
		timeout = -1
		for timer in self.timers:
			if timeout > timer.countdown() or timout == -1:
					timeout = timer.countdown()

		return timeout

	def emit(self, event, data=None):
		if event not in self.event_handlers:
			self.event_handlers[event] = []
		for handler in self.event_handlers[event]:
			handler(event, (data.clone() if data else data))

	def reg_event_handler(self, events, handlers):
		if isinstance(events, str) or not hasattr(events, '__iter__'): 
			events = [events]
		if not hasattr(handlers, '__iter__'):
			handlers = [handlers]

		for event in events:
			if event not in self.event_handlers:
				self.event_handlers[event] = []
			self.event_handlers[event].extend(handlers)

	def register_timer(self, timer):
		self.timers.append(timer)

	def kill(self):
		self.emit('kill')
		self.kill = True

	def reset(self):
		self.sock.close()
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.setblocking(0)

	def signal_handler(self, *args):
		self.kill = True
