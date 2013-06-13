import math
from spock.net.packet_handlers import phandles, PositionUpdate
from spock.mcp.mcpacket import Packet

class GravityPlugin:
	def __init__(self, client):
		self.client = client
		for ident, handler in phandles.iteritems():
			if handler == PositionUpdate:
				client.register_dispatch(self.fall, ident)
		client.register_dispatch(self.fall, 0x33)
		client.register_dispatch(self.fall, 0x38)

	def fall(self, packet):
		print("Entering fall func")
		if not self.client.position['on_ground']:
			print("Trying to Fall")
			y = int(math.floor(self.client.position['y']))
			x = int(math.floor(self.client.position['x']))
			z = int(math.floor(self.client.position['z']))
			ground = self.findground(x, y, z)
			if ground == -1:
				return
			if (self.client.position['y']-ground)>1:
				self.client.push(Packet(ident = 0x0B, data = {
					'x': self.client.position['x'],
					'y': (self.client.position['y']-1),
					'z': self.client.position['z'],
					'stance': (self.client.position['stance']-1),
					'on_ground': False,
					}))
			else:
				self.client.push(Packet(ident = 0x0B, data = {
					'x': self.client.position['x'],
					'y': (ground+1),
					'z': self.client.position['z'],
					'stance': (ground+2),
					'on_ground': True,
					}))

	def findground(self, x,y,z):
		blockid = 0
		while not blockid:
			blockid = self.client.world.get(x, y, z, 'block_data')
			y -= 1
			if y == -1: break
		return y