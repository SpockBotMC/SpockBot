PHYSICS_TICK = 0.02

class PhysicsPlugin:
	def __init__(self):
		self.world = ploader.requires('World')
		self.timer = ploader.requires('Timer')
		self.timer.reg_event_timer(PHYSICS_TICK, self.tick, -1)

	def tick(self):
		pass
