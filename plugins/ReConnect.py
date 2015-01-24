"""
On a disconnect event, reconnects to the last connected server
"""
from spock.mcp import mcpacket, mcdata

class ReConnectPlugin:
	def __init__(self, ploader, settings):
		self.reconnecting = False
		self.host = None
		self.port = None
		ploader.reg_event_handler('connect', self.connect)
		ploader.reg_event_handler('disconnect', self.reconnect_event)
		self.net = ploader.requires('Net')
		self.timers = ploader.requires('Timers')
		self.auth = ploader.requires('Auth')
	
	def connect(self, event, data):
		self.host = data[0]
		self.port = data[1]

	def reconnect_event(self, event, data):
		print("DISCONNECT EVENT")
		if not self.reconnecting:
			self.timers.reg_event_timer(1, self.reconnect, 1, True)

	def reconnect(self):
		print("RECONNECT FUNC")
		self.net.connect(self.host, self.port)
		self.net.push(mcpacket.Packet(
			ident = (mcdata.HANDSHAKE_STATE, mcdata.CLIENT_TO_SERVER, 0x00),
			data = {
				'protocol_version': mcdata.MC_PROTOCOL_VERSION,
				'host': self.net.host,
				'port': self.net.port,
				'next_state': mcdata.LOGIN_STATE
			}
		))

		self.net.push(mcpacket.Packet(
			ident = (mcdata.LOGIN_STATE, mcdata.CLIENT_TO_SERVER, 0x00),
			data = {'name': self.auth.username},
		))
