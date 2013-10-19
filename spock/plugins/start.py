"""
This plugin creates a convenient start() method and attaches it directly
to the client. More complex bots will likely want to create their own
initialization plugin, so StartPlugin stays out of the way unless you
call the start() method. However, the start() method is very convenient
for demos and tutorials, and illustrates the basic steps for initializing
a bot.
"""

from spock.mcp import mcpacket, mcdata

class StartPlugin:
	def __init__(self, ploader, settings):
		self.net = ploader.requires('Net')
		self.auth = ploader.requires('Auth')
		self.client = ploader.requires('Client')

		setattr(self.client, 'start', self.start)

	def start(self, host = 'localhost', port = 25565):
		if 'error' not in self.auth.start_session(
			self.client.mc_username, 
			self.client.mc_password
		):
			self.net.connect(host, port)
			self.handshake()
			self.client.event_loop()
		self.net.disconnect()

	def handshake(self):
		self.net.push(mcpacket.Packet(ident = 0x02, data = {
			'protocol_version': mcdata.MC_PROTOCOL_VERSION,
			'username': self.auth.username,
			'host': self.net.host,
			'port': self.net.port,
			})
		)