"""
Hilariously out of date, I'll update this when it's not 3:30 in the morning
In the meantime, go look at plugins in spock.net.plugins for more up-to-date plugin examples
"""

from spock.mcp.mcpacket import Packet
from spock.net.cflags import cflags
from spock.net.timer import EventTimer

#Will relentlessly try to reconnect to a server
class ReConnectPlugin:
	def __init__(self, client, settings):
		self.client = client
		self.lock = False
		self.kill = False
		self.delay = 0

		client.register_handler(self.start_timer, cflags['SOCKET_ERR'], cflags['SOCKET_HUP'])
		client.register_handler(self.stop, cflags['KILL_EVENT'])
		client.register_dispatch(self.start_timer, 0xFF)
		client.register_dispatch(self.grab_host, 0x02)
		client.register_dispatch(self.reset_reconnect_time, 0x01)

	def start_timer(self, *args):
		if not self.lock:
			self.client.register_timer(EventTimer(self.delay, self.reconnect))
			self.lock = True

	def stop(self, *args):
		self.kill = True

	def reconnect(self, *args):
		if not self.kill:
			if self.delay < 300:
				self.delay += 30
			self.client.start_session(self.client.mc_username, self.client.mc_password)
			self.client.login(self.host, self.port)
			self.lock = False

	def reset_reconnect_time(self, *args):
		self.delay = 0

	#Grabs host and port on handshake
	def grab_host(self, packet):
		self.host = packet.data['host']
		self.port = packet.data['port']
