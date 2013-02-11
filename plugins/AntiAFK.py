from spock.mcp.mcpacket import Packet
from copy import copy

#Very bad and naive Anti-AFK plugin
class AntiAFKPlugin:
	def __init__(self, client):
		self.client = client
		client.register_dispatch(self.avoid_afk, 0x03)
		self.sentinal = True

	def avoid_afk(self, packet):
		msg = packet.data['text'].lower()
		if ('afk' in msg) or ('inactivity' in msg):
			newposition = self.client.position
			if self.sentinal:
				newposition['x']+=1
				self.sentinal = False
			else:
				newposition['x']-=1
				self.sentinal = True		
			self.client.push(Packet(ident=0x0D, data=newposition))