"""
PhysicsPlugin is planned to provide vectors and tracking necessary to implement
SMP-compliant client-side physics for entities. Primarirly this will be used to
keep update client position for gravity/knockback/water-flow etc. But it should
also eventually provide functions to track other entities affected by SMP
physics
"""


class PhysicsPlugin:
	def __init__(self):
		self.world = ploader.requires('World')

	def tick(self):
		pass
