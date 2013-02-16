from spock.mcp.mcpacket import Packet
from spock.net.cflags import cflags

#Will try relentlessly to reconnect to a server
class ReConnectPlugin:
	def __init__(self, client):
		self.client = client
		client.register_handler(self.flag_reconnect, cflags['SOCKET_ERR'])
		client.register_handler(self.flag_reconnect, cflags['SOCKET_HUP'])
		client.register_dispatch(self.packet_reconnect, 0xFF)
		client.register_dispatch(self.grab_host, 0x02)

	def packet_reconnect(self, packet):
		self.client.login(self.host, self.port)

	def flag_reconnect(self):
		self.client.login(self.host, self.port)

	#Grabs host and port on handshake
	def grab_host(self, packet):
		self.host = self.client.host
		self.port = self.client.port
