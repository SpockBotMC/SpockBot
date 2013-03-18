from spock.mcp.mcpacket import Packet
from spock.net.cflags import cflags

#Will relentlessly try to reconnect to a server
class ReConnectPlugin:
	def __init__(self, client):
		self.client = client
		self.kill = False
		client.register_handler(self.session_reconnect, cflags['AUTH_ERR'])
		client.register_handler(self.reconnect, cflags['SOCKET_ERR'], cflags['SOCKET_HUP'])
		client.register_handler(self.stop, cflags['KILL_EVENT'])
		client.register_dispatch(self.reconnect, 0xFF)
		client.register_dispatch(self.grab_host, 0x02)
		client.register_dispatch(self.reset_reconnect_time, 0x01)
		self.reset_reconnect_time()

	def session_reconnect(self, *args):
		if not self.kill:
			self.client.start_session(self.client.mc_username, self.client.mc_password)
			self.client.login(self.host, self.port)

	def reconnect(self, *args):
		if not self.kill:
			sleep(self.delay)
			if self.delay < 300:
				self.delay = self.delay * 2
			self.client.login(self.host, self.port)

	def reset_reconnect_time(self, *args):
		self.delay = 1.18

	#Grabs host and port on handshake
	def grab_host(self, packet):
		self.host = packet.data['host']
		self.port = packet.data['port']

	def stop(self, *agrs):
		self.kill = True
