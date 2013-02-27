import spock.net.client
from spock.net.timer import ThreadedTimer, TickTimer
from packet_queue import PacketQueue

class RikerClient(spock.net.client.Client):
	def __init__(self):
		super(RikerClient, self).__init__()
		self.move_queue = PacketQueue()
		ThreadedTimer(.05, self._send_move, -1).start()
		self.register_timer(TickTimer(self, 6000, self._keep_session_alive, -1))

	def push_move(self, packet):
		self.move_queue.push(packet)

	def _send_move(self):
		if self.move_queue:
			self.push(self.move_queue.pop())

	def move_to(x, y, z):
		pass