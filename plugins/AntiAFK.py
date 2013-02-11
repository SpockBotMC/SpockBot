from spock.mcp.mcpacket import Packet

#Very bad and naive Anti-AFK plugin
class AntiAFKPlugin:
	def __init__(self, client):
		self.client = client
		client.register_dispatch(self.avoid_afk, 0x03)

	def avoid_afk(self, packet):
		msg = packet.data['text'].lower()
		if ('afk' in msg) or ('inactivity' in msg):
			oldposition = client.position
			newposition = client.position
			newposition['x']+=1
			client.push(Packet(ident=0x0D, data=newposition))
			client.push(Packet(ident=0x0D, data=oldposition))