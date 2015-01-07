"""
PhysicsPlugin is planned to provide vectors and tracking necessary to implement
SMP-compliant client-side physics for entities. Primarirly this will be used to
keep update client position for gravity/knockback/water-flow etc. But it should
also eventually provide functions to track other entities affected by SMP
physics

Minecraft client/player physics is unfortunately very poorly documented. Most of
these values are based of experimental results and the contributions of a
handful of people (Thank you 0pteron!) to the Minecraft wiki talk page on
Entities and Transportation. Ideally someone will decompile the client with MCP
and document the totally correct values and behaviors.
"""

#Gravitational constants defined in blocks/(client tick)^2
PLAYER_ENTITY_GAV = 0.08
THROWN_ENTITY_GAV = 0.03
RIDING_ENTITY_GAV = 0.04
BLOCK_ENTITY_GAV  = 0.04
ARROW_ENTITY_GAV  = 0.05

#Drag constants defined in 1/tick for same physics and client tick
PLAYER_ENTITY_DRG = 0.02
THROWN_ENTITY_DRG = 0.01
RIDING_ENTITY_DRG = 0.05
BLOCK_ENTITY_DRG  = 0.02
ARROW_ENTITY_DRG  = 0.01

#Player ground acceleration isn't actually linear, but we're going to pretend
#that it is. Max ground velocity for a walking client is 0.215blocks/tick, it
#takes a dozen or so ticks to get close to max velocity. Sprint is 0.28, just
#apply more acceleration to reach a higher max ground velocity
PLAYER_WLK_ACC    = 0.15
PLAYER_SPR_ACC    = 0.20
PLAYER_GND_DRG    = 0.41

class Vec3:
	def __init__(self, x, y, z):
		self.x = x
		self.y = y
		self.z = z

	def add_vector(self, x = None, y = None, z = None, vec = None):
		if vec:
			self.x += vec.x
			self.y += vec.y
			self.z += vec.z
		else:
			if x: self.x += x
			if y: self.y += y
			if z: self.z += z

class PhysicsPlugin:
	def __init__(self, ploader, settings):
		self.vec = Vec3(0, 0, 0)
		self.world = ploader.requires('World')
		clinfo = ploader.requires('ClientInfo')
		self.pos = clinfo.position
		ploader.reg_event_handler('physics_tick', self.tick)

	def tick(self, _, __):
		p = self.pos
		floor = self.world.get_floor(p['x'], p['y'], p['z'])
		if p['y'] != floor:
			p['on_ground'] = False
			self.vec.add_vector(y = -PLAYER_ENTITY_GAV)
			self.apply_drag()
			if p['y'] + self.vec.y <= floor:
				p['on_ground'] = True
				self.vec.y = 0
				p['y'] = floor
		self.apply_vector()

	#TODO: Apply drag to actual velocity not just vertical velocity
	#TODO: Apply drag to ground movement
	def apply_drag(self):
		p = self.pos
		self.vec.y = self.vec.y - self.vec.y*PLAYER_ENTITY_DRG

	def apply_vector(self):
		p = self.pos
		p['x'] = p['x'] + self.vec.x
		p['y'] = p['y'] + self.vec.y
		p['z'] = p['z'] + self.vec.z
