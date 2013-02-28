import threading
from spock.mcp.mcpacket import Packet
from spock.net.cflags import cflags
from spock.net.timer import ThreadedTimer

class NoLaggPlugin:
	def __init__(self, client):
		self.client = client
		self.packet = Packet(ident = 0x03, data = {
			"text": "/nolagg monitor"
			})
		self.stop_event = threading.Event()
		client.register_dispatch(self.start_timer, 0x02)
		client.register_handler(self.stop_timer, cflags['SOCKET_ERR'], cflags['SOCKET_HUP'], cflags['KILL_EVENT'])
		client.register_dispatch(self.stop_timer, 0xFF)

	def start_timer(self, *args):
		self.stop_event.clear()
		ThreadedTimer(self.stop_event, 20, self.start_nolagg, -1).start()

	def stop_timer(self, *args):
		self.stop_event.set()

	def start_nolagg(self, *args):
		self.client.push(self.packet)
		ThreadedTimer(self.stop_event, 10, self.stop_nolagg).start()

	def stop_nolagg(self, *args):
		self.client.push(self.packet)
