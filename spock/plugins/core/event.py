"""
Provides the core event loop
"""

import signal
import copy
from spock.mcp import mcdata
from spock.utils import pl_announce

class EventCore:
	def __init__(self):
		self.kill_event = False
		self.event_handlers = {}

	def event_loop(self):
		signal.signal(signal.SIGINT, self.kill)
		signal.signal(signal.SIGTERM, self.kill)
		while not self.kill_event:
			self.emit('event_tick')
		self.emit('kill')

	def reg_event_handler(self, event, handler):
		if event not in self.event_handlers:
			self.event_handlers[event] = []
		self.event_handlers[event].append(handler)

	def emit(self, event, data = None):
		if event not in self.event_handlers:
			self.event_handlers[event] = []
		for handler in self.event_handlers[event]:
			handler(event, (data.clone() if hasattr(data, 'clone')
				else copy.deepcopy(data)
			))

	def kill(self, *args):
		self.kill_event = True

@pl_announce('Event')
class EventPlugin:
	def __init__(self, ploader, settings):
		ploader.provides('Event', EventCore())
