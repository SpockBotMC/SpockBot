import time

class Timer(object):
	def __init__(self, wait_time, callback, runs = 1):
		self.runs = runs
		self.callback = callback
		self.wait_time = wait_time
		self.end_time = time.time() + self.wait_time

	def update(self):
		if self.runs == 0: return False
		return self.end_time<=time.time()

	def check(self):
		return bool(self.runs)

	def fire(self):
		self.callback()
		if self.runs>0: self.runs-=1


	def reset(self):
		self.end_time = time.time() + self.wait_time

