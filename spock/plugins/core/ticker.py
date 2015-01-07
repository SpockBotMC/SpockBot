"""
Registers timers to provide the necessary tick rates expected by MC servers
"""

CLIENT_TICK_RATE = 0.05

class TickerPlugin:
	def __init__(self, ploader, settings):
		self.event = ploader.requires('Event')
		self.timers = ploader.requires('Timers')
		ploader.reg_event_handler('PLAY_STATE', self.start_tickers)

	def start_tickers(self, _, __):
		self.timers.reg_event_timer(CLIENT_TICK_RATE, self.client_tick)

	def client_tick(self):
		self.event.emit('physics_tick')
		self.event.emit('client_tick')
