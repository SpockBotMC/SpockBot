from spock.mcp.mcpacket import Packet

#Very bad and naive Anti-AFK plugin
class AntiAFKPlugin:
	def __init__(self, client):
		self.client = client
		client.register_dispatch(self.avoid_afk, 0x03)
		client.register_dispatch(self.revive, 0x08)

	def avoid_afk(self, packet):
		msg = packet.data['text'].lower()
		if ('afk plugin' in msg):
			self.client.push(Packet(ident=0x03, data={
				"text": "Hello, I am Spock_Bot, this message is to avoid AFKGC"
				})
			)

	def revive(self, packet):
		if self.client.health['health']<=0:
			self.client.push(Packet(ident=0xCD, data={'payload': 1}))
