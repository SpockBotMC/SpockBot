from spock.mcp.mcpacket import Packet
from spock.net.timer import ThreadedTimer

class AntiAFKPlugin:
	def __init__(self, client):
		time = 300
		timer = ThreadedTimer(300, self.send_nolagg, -1)
		self.client = client

		timer.start()

	def send_nolagg(self):
		packet = Packet(ident = 0x03, data = {
			"text": "/nolagg monitor"
			})
		self.client.push(packet)
		self.client.push(packet)