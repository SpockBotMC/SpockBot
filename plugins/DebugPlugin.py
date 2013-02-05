#Constantly Changing, just a plugin I use to debug whatever is broken atm

class DebugPlugin:
	def __init__(self, client):
		self.client = client
		for ident in structs:
			client.register_dispatch(self.debug, ident)
	def debug(self, packet):
		if packet.ident == 0xC9 or packet.ident == 0x03: print packet