import time
from spock.plugins.plutils import pl_announce

class BaseTimer(object):
	def __init__(self, callback, runs = 1):
		self.callback = callback
		self.runs = runs

	def get_runs(self):
		return self.runs

	def update(self):
		if self.check():
			self.fire()

	def fire(self):
		self.callback()
		if self.runs>0:
			self.runs-=1
		if self.runs:
			self.reset()

	def stop(self):
		self.runs = 0

#Time based timer
class EventTimer(BaseTimer):
	def __init__(self, wait_time, callback, runs = 1):
		super().__init__(callback, runs)
		self.wait_time = wait_ticks
		self.end_time = time.time() + self.wait_time

	def countdown(self):
		return self.end_time - time.time()

	def check(self):
		if self.runs == 0: return False
		return self.end_time<=time.time()

	def reset(self):
		self.end_time = time.time() + self.wait_time

#Tick based timer
class TickTimer(BaseTimer):
	def __init__(self, world, wait_ticks, callback, runs = 1):
		super().__init__(callback, runs)
		self.world = world
		self.wait_ticks = wait_ticks
		self.end_tick = self.world.age + self.wait_ticks

	def countdown(self):
		return -1

	def check(self):
		if self.runs == 0: return False
		return self.end_tick<=self.world.age

	def reset(self):
		self.end_tick = self.world.age + self.wait_ticks

class TimerInterface:
	def __init__(self, reg_timer, world):
		self.reg_timer = reg_timer
		self.world = world

	def reg_event_timer(self, wait_time, callback, runs = 1):
		self.reg_timer(EventTimer(wait_time, callback, runs))

	def reg_tick_timer(self, wait_ticks, callback, runs = 1):
		self.reg_timer(TickTimer(self.world, wait_ticks, callback, runs))

@pl_announce('Timers')
class TimerPlugin:
	def __init__(self, ploader, settings):
		self.client = ploader.requires('Client')
		ploader.provides('Timers', 
			TimerInterface(
				self.client.reg_timer,
				ploader.requires('World')
			)
		)
		ploader.reg_event_handler(
			(0xFF, 'SOCKET_ERR', 'SOCKET_HUP'),
			self.handle_disconnect
		)

	def handle_disconnect(self, name, data):
		self.client.timers = []