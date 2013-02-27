import time

class Timer(object):
	def __init__(self, wait_time, callback):
		self.callback = callback
		self.time = time.time() + wait_time

	def check(self):
		return self.time<=time.time()

	def fire(self):
		self.callback()