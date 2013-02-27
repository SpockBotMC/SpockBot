import time
import threading

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

class ThreadedTimer(threading.Thread):
	def __init__(self, wait_time, callback, runs = 1):
		super(ThreadedTimer, self).__init__()
		self.wait_time = wait_time
		self.callback = callback
		self.runs = runs
		self.start()

	def run(self):
		while self.runs:
			time.sleep(self.wait_time)
			self.callback()
			if self.runs:
				self.runs-=1

