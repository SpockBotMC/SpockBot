"""
KeepalivePlugin is a pretty cool guy. Eh reflects keep alive packets and doesnt
afraid of anything.
"""

from spock.mcp import mcdata, mcpacket

class KeepalivePlugin:
	def __init__(self, ploader, settings):
		self.net = ploader.requires('Net')
		ploader.reg_event_handler('PLAY<Keep Alive', self.handle_keep_alive)

	#Keep Alive - Reflects data back to server
	def handle_keep_alive(self, name, packet):
		packet.new_ident('PLAY>Keep Alive')
		self.net.push(packet)
