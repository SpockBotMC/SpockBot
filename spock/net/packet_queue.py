from collections import deque
from mcp.packet import read_bytes

class PacketQueue:
	def __init__(self, *args):
		self.queue = (deque(args[0]) if args else deque())

	def push(self, packet):
		self.buff.append(packet)

	def pushbytes(self, data):
		self.buff.append(read_bytes(data))

	def pop(self):
		return self.buff.popleft()

	def popbytes(self):
		p = self.buff.popleft()
		return p.encode()