import time
import threading

#Time based timer handled by the client
class EventTimer(object):
	def __init__(self, wait_time, callback, runs = 1):
		self.wait_time = wait_time
		self.callback = callback
		self.runs = runs
		self.end_time = time.time() + self.wait_time

	def update(self):
		if self.runs == 0: return False
		return self.end_time<=time.time()

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

	def reset(self):
		self.end_time = time.time() + self.wait_time

#Tick based timer handled by the client
class TickTimer(object):
	def __init__(self, client, wait_ticks, callback, runs = 1):
		self.client = client
		self.wait_ticks = wait_ticks
		self.callback = callback
		self.runs = runs
		self.end_tick = client.world_time['world_age'] + self.wait_ticks

	def update(self):
		if self.runs == 0: return False
		return self.end_tick<=self.client.world_time['world_age']

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

	def reset(self):
		self.end_tick = self.client.world_time['world_age'] + self.wait_ticks

#Time based timer handled in a seperate thread, does not need to be registered with the client
#Threaded timers can be very tricky with daemon code, only use if you know what you're doing
class ThreadedTimer(threading.Thread):
	def __init__(self, stop_event, wait_time, callback, runs = 1):
		super(ThreadedTimer, self).__init__()
		self.stop_event = stop_event
		self.wait_time = wait_time
		self.callback = callback
		self.runs = runs

	def run(self):
		while not self.stop_event.is_set() and self.runs:
			self.stop_event.wait(self.wait_time)
			if not self.stop_event.is_set():
				self.callback()
				if self.runs>0:
					self.runs-=1
