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
		return bool(self.runs)

	def fire(self):
		self.callback()
		if self.runs:
			self.runs-=1
			self.reset()

	def reset(self):
		self.end_time = time.time() + self.wait_time

#Tick based timer handled by the client
class TickTimer(object):
	def __init__(self, client, wait_ticks, callback, runs =1):
		self.client = client
		self.wait_ticks = wait_ticks
		self.callback = callback
		self.runs = runs
		self.end_tick = client.world_time['world_age'] + self.wait_ticks

	def update(self):
		if self.runs == 0: return False
		return self.end_tick<=self.client.world_time['world_age']

	def check(self):
		return bool(self.runs)

	def fire(self):
		self.callback()
		if self.runs:
			self.runs-=1
			self.reset()

	def reset(self):
		self.end_tick = self.client.world_time['world_age'] + self.wait_ticks

#Time based timer handled in a seperate thread
#This timer does not need to be registered with the client
class ThreadedTimer(threading.Thread):
	def __init__(self, wait_time, callback, runs = 1):
		super(ThreadedTimer, self).__init__()
		self.wait_time = wait_time
		self.callback = callback
		self.runs = runs

	def run(self):
		while self.runs:
			time.sleep(self.wait_time)
			self.callback()
			if self.runs:
				self.runs-=1
