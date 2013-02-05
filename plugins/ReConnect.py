import socket
from spock.mcp.mcpacket import Packet

#Naive and enthusiatic attempt to reconnect to a server
#Will only work if the client recieved a 0xFF first
class ReConnectPlugin:
	def __init__(self, client):
		self.client = client
		client.register_dispatch(self.reconnect, 0xFF)
		client.register_dispatch(self.grab_host, 0x02)
	def reconnect(self, packet):
		print "Attempting reconnect"
		self.client.login(self.host, self.port)
	#Grabs host and port on handshake
	def grab_host(self, packet):
		self.host = self.client.host
		self.port = self.client.port