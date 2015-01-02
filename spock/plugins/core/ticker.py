CLIENT_TICK_RATE = 0.05
PHYSICS_TICK_RATE = 0.02

class TickerPlugin:
	def __init__(self, ploader, settings):
		self.event = ploader.requires("Event")
		self.timers = ploader.requires("Timers")
		self.timers.reg_event_timer(CLIENT_TICK_RATE, self.client_tick, -1)
		self.timers.reg_event_timer(PHYSICS_TICK_RATE, self.physics_tick, -1)

	def client_tick(self):
		self.event.emit('client_tick')

	def physics_tick(self):
		self.event.emit('physics_tick')