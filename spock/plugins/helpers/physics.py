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
from spock.mcmap import mapdata

#Gravitational constants defined in blocks/(client tick)^2
PLAYER_ENTITY_GAV = 0.08
THROWN_ENTITY_GAV = 0.03
RIDING_ENTITY_GAV = 0.04
BLOCK_ENTITY_GAV  = 0.04
ARROW_ENTITY_GAV  = 0.05

#Air drag constants defined in 1/tick
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

#Seems about right, not based on anything
PLAYER_JMP_ACC    = 0.45

import math
from spock.utils import pl_announce

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

	def __str__(self):
		return "({:.2f}, {:.2f}, {:.2f})".format(self.x, self.y, self.z)

class BoundingBox:
	def __init__(self, w, h, d=None):
		self.w = w #x
		self.h = h #y
		if d:
			self.d = d #z
		else:
			self.d = w

class PhysicsCore:
	def __init__(self, vec, pos):
		self.vec = vec
		self.pos = pos

	def jump(self):
		if self.pos.on_ground:
			self.pos.on_ground = False
			self.vec.add_vector(y = PLAYER_JMP_ACC)

	def walk(self, angle, radians = False):
		if self.pos.on_ground:
			if not radians:
				angle = math.radians(angle)
			z = math.cos(angle)*PLAYER_WLK_ACC
			x = math.sin(angle)*PLAYER_WLK_ACC
			self.vec.add_vector(x = x, z = z)

	def sprint(self, angle, radians = False):
		if self.pos.on_ground:
			if not radians:
				angle = math.radians(angle)
			z = math.cos(angle)*PLAYER_SPR_ACC
			x = math.sin(angle)*PLAYER_SPR_ACC
			self.vec.add_vector(x = x, z = z)


@pl_announce('Physics')
class PhysicsPlugin:
	def __init__(self, ploader, settings):
		self.vec = Vec3(0.0, 0.0, 0.0)
		self.playerbb = BoundingBox(0.8, 1.8) #wiki says 0.6 but I made it 0.8 to give a little wiggle room
		self.world = ploader.requires('World')
		clinfo = ploader.requires('ClientInfo')
		self.pos = clinfo.position
		ploader.reg_event_handler('physics_tick', self.tick)
		ploader.provides('Physics', PhysicsCore(self.vec, self.pos))

	def tick(self, _, __):
		self.check_collision()
		self.apply_gravity()
		self.apply_horizontal_drag()
		self.apply_vector()

	def check_collision(self):
		cb = Vec3(math.floor(self.pos.x), math.floor(self.pos.y), math.floor(self.pos.z))
		#feet or head collide with x
		if self.block_collision(cb, x=1) or self.block_collision(cb, x=-1) or self.block_collision(cb, y=1, x=1) or self.block_collision(cb, y=1, x=-1):
			self.vec.x = 0
		#feet or head collide with z
		if self.block_collision(cb, z=1) or self.block_collision(cb, z=-1) or self.block_collision(cb, y=1, z=1) or self.block_collision(cb, y=1, z=-1):
			self.vec.z = 0
		#neg y is handled by apply_gravity
		if self.block_collision(cb, y=2): #we check +2 because above my head
			self.vec.y = 0

	def block_collision(self, cb, x = 0, y = 0, z = 0):
		block_id, _ = self.world.get_block(cb.x+x, cb.y+y, cb.z+z)
		#possibly we want to use the centers of blocks as the starting points for bounding boxes instead of 0,0,0
		#this might make thinks easier when we get to more complex shapes that are in the center of a block aka fences but more complicated for the player
		#uncenter the player position
		pos1 = Vec3(self.pos.x-self.playerbb.w/2, self.pos.y, self.pos.z-self.playerbb.d/2)
		bb1 = self.playerbb
		pos2 = Vec3(cb.x+x, cb.y+y, cb.z+z)
		bb2 = self.get_bounding_box(block_id)
		if bb2 != None:
			if ((pos1.x + bb1.w) >= (pos2.x) and (pos1.x) <= (pos2.x + bb2.w)) and \
				((pos1.y + bb1.h) >= (pos2.y) and (pos1.y) <= (pos2.y + bb2.h)) and \
				((pos1.z + bb1.d) >= (pos2.z) and (pos1.z) <= (pos2.z + bb2.d)):
				return True
		return False

	def get_bounding_box(self, blockid):
		if blockid in mapdata.NON_COLLISION_BLOCKS:
			return None
		else:
			return BoundingBox(1,1)

	def apply_gravity(self):
		p = self.pos
		floor = self.world.get_floor(p.x, p.y, p.z)
		if p.y != floor:
			p.on_ground = False
			self.vec.add_vector(y = -PLAYER_ENTITY_GAV)
			self.apply_vertical_drag()
			if p.y + self.vec.y <= floor:
				p.on_ground = True
				self.vec.y = 0
				p.y = floor

	def apply_vertical_drag(self):
		self.vec.y = self.vec.y - self.vec.y*PLAYER_ENTITY_DRG

	def apply_horizontal_drag(self):
		if self.pos.on_ground:
			self.vec.x = self.vec.x - self.vec.x*PLAYER_GND_DRG
			self.vec.z = self.vec.z - self.vec.z*PLAYER_GND_DRG
		else:
			self.vec.x = self.vec.x - self.vec.x*PLAYER_ENTITY_DRG
			self.vec.z = self.vec.z - self.vec.z*PLAYER_ENTITY_DRG

	def apply_vector(self):
		p = self.pos
		p.x = p.x + self.vec.x
		p.y = p.y + self.vec.y
		p.z = p.z + self.vec.z
