from collections import deque

#Stupid little fifo wrapper around deque
class PacketQueue(object):
	def __init__(self, *args):
		self.queue = (deque(args[0]) if args else deque())

	def push(self, packet):
		self.queue.append(packet)

	def pop(self):
		return self.queue.popleft()

	def __len__(self):
		return self.queue.__len__()