from collections import deque
from spock.mcp.packet import read_bytes

class PacketQueue:
	def __init__(self, *args):
		self.queue = (deque(args[0]) if args else deque())

	def push(self, packet):
		self.queue.append(packet)

	def pushbytes(self, data):
		self.queue.append(read_bytes(data))

	def pop(self):
		return self.queue.popleft()

	def popbytes(self):
		p = self.queue.popleft()
		return p.encode()

	def __len__(self):
		return self.queue.__len__()