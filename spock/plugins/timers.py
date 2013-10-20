import time
from spock.plugins.plutils import pl_announce

class BaseTimer(object):
	def __init__(self, callback, runs = 1):
		self.callback = callback
		self.runs = runs

	def check(self):
		return self.runs

	def fire(self):
		self.callback()
		if self.runs>0:
			self.runs-=1
		if self.runs:
			self.reset()

	def stop(self):
		self.runs = 0

#Time based timer handled by the client
class EventTimer(BaseTimer):
	def __init__(self, wait_time, callback, runs = 1):
		super().__init__(callback, runs)
		self.wait_time = wait_ticks
		self.end_time = time.time() + self.wait_time

	def update(self):
		if self.runs == 0: return False
		return self.end_time<=time.time()

	def countdown(self):
		return self.end_time - time.time()

	def reset(self):
		self.end_time = time.time() + self.wait_time

#Tick based timer handled by timer plugin
class TickTimer(BaseTimer):
	def __init__(self, world, wait_ticks, callback, runs = 1):
		super().__init__(callback, runs)
		self.world = world
		self.wait_ticks = wait_ticks
		self.end_tick = self.world.age + self.wait_ticks

	def update(self):
		if self.runs == 0: return False
		return self.end_tick<=self.world.age

	def reset(self):
		self.end_tick = self.world.age + self.wait_ticks

class TimerInterface:
	pass

@pl_announce('Timers')
class TimerPlugin:
	pass