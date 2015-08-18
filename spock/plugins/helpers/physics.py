"""
PhysicsPlugin is planned to provide vectors and tracking necessary to implement
SMP-compliant client-side physics for entities. Primarirly this will be used to
keep update client position for gravity/knockback/water-flow etc. But it should
also eventually provide functions to track other entities affected by SMP
physics

Minecraft client/player physics is unfortunately very poorly documented.
Most of
these values are based of experimental results and the contributions of a
handful of people (Thank you 0pteron!) to the Minecraft wiki talk page on
Entities and Transportation. Ideally someone will decompile the client with MCP
and document the totally correct values and behaviors.
"""
# Gravitational constants defined in blocks/(client tick)^2
PLAYER_ENTITY_GAV = 0.08
THROWN_ENTITY_GAV = 0.03
RIDING_ENTITY_GAV = 0.04
BLOCK_ENTITY_GAV = 0.04
ARROW_ENTITY_GAV = 0.05

# Air drag constants defined in 1/tick
PLAYER_ENTITY_DRG = 0.02
THROWN_ENTITY_DRG = 0.01
RIDING_ENTITY_DRG = 0.05
BLOCK_ENTITY_DRG = 0.02
ARROW_ENTITY_DRG = 0.01

# Player ground acceleration isn't actually linear, but we're going to pretend
# that it is. Max ground velocity for a walking client is 0.215blocks/tick, it
# takes a dozen or so ticks to get close to max velocity. Sprint is 0.28, just
# apply more acceleration to reach a higher max ground velocity
PLAYER_WLK_ACC = 0.15
PLAYER_SPR_ACC = 0.20
PLAYER_GND_DRG = 0.41

# Seems about right, not based on anything
PLAYER_JMP_ACC = 0.45

import logging
import math
import queue

from spock.mcmap import mapdata
from spock.plugins.base import PluginBase
from spock.utils import BoundingBox, Position, pl_announce
from spock.vector import Vector3

logger = logging.getLogger('spock')

class PhysicsCore(object):
    def __init__(self, vec, pos):
        self.vec = vec
        self.pos = pos

    def jump(self):
        if self.pos.on_ground:
            self.vec.y += PLAYER_JMP_ACC

    def walk(self, angle, radians=False):
        angle = angle if radians else math.radians(angle)
        z = math.cos(angle) * PLAYER_WLK_ACC
        x = math.sin(angle) * PLAYER_WLK_ACC
        self.vec.z += z
        self.vec.x += x

    def sprint(self, angle, radians=False):
        angle = angle if radians else math.radians(angle)
        z = math.cos(angle) * PLAYER_SPR_ACC
        x = math.sin(angle) * PLAYER_SPR_ACC
        self.vec.z += z
        self.vec.x += x

@pl_announce('Physics')
class PhysicsPlugin(PluginBase):
    requires = ('Event', 'ClientInfo', 'World')
    events = {
        'physics_tick': 'tick',
    }
    unit_vectors = Vector3(1, 0, 0), Vector3(0, 1, 0), Vector3(0, 0, 1)

    def __init__(self, ploader, settings):
        super(PhysicsPlugin, self).__init__(ploader, settings)
        self.vec = Vector3(0.0, 0.0, 0.0)
        self.playerbb = BoundingBox(0.6, 1.8)
        self.pos = self.clientinfo.position
        ploader.provides('Physics', PhysicsCore(self.vec, self.pos))

    def tick(self, _, __):
        self.vec.y -= PLAYER_ENTITY_GAV
        self.apply_drag()
        mtv = self.get_mtv()
        self.pos.on_ground = mtv.y > 0
        self.apply_vector(mtv)

    def apply_drag(self):
        self.vec.y -= self.vec.y * PLAYER_ENTITY_DRG
        self.vec.x -= self.vec.x * PLAYER_GND_DRG
        self.vec.z -= self.vec.z * PLAYER_GND_DRG

    def apply_vector(self, mtv):
        self.vec += mtv
        self.pos += self.vec

    def gen_block_position(self, pos):
        x = math.floor(pos.x)
        y = math.floor(pos.y)
        z = math.floor(pos.z)
        return Position(x, y, z)

    def gen_block_set(self, block_pos):
        offsets = ((x,y,z) for x in (-1,0,1) for y in (0,1,2) for z in (-1,0,1))
        return (block_pos - Vector3(*offset) for offset in offsets)

    def check_collision(self, pos, vector):
        test_pos = pos + vector
        center_block_pos = self.gen_block_position(test_pos)
        return self.block_collision(center_block_pos, test_pos)

    # Breadth-first search for a minimum translation vector
    def get_mtv(self):
        pos = self.pos + self.vec
        pos.x -= self.playerbb.w/2
        pos.z -= self.playerbb.d/2
        current_vector = Vector3()
        transform_vectors = []
        q = queue.Queue()
        while all(transform_vectors) or q.empty():
            current_vector = q.get() if not q.empty() else current_vector
            transform_vectors = self.check_collision(pos, current_vector)
            for vector in transform_vectors:
                q.put(current_vector + vector)
        possible_mtv = [current_vector]
        while not q.empty():
            current_vector = q.get()
            transform_vectors = self.check_collision(pos, current_vector)
            if not all(transform_vectors):
                possible_mtv.append(current_vector)
        return min(possible_mtv)

    def block_collision(self, center_block_pos, pos):
        for block_pos in self.gen_block_set(center_block_pos):
            block_id, meta = self.world.get_block(block_pos.x, block_pos.y, block_pos.z)
            block = mapdata.get_block(block_id, meta)
            if not block.bounding_box:
                continue
            transform_vectors = []
            for i, axis in enumerate(self.unit_vectors):
                axis_pen = self.test_axis(axis, pos[i], pos[i] + self.playerbb[i],
                    block_pos[i], block_pos[i] + block.bounding_box[i])
                if not axis_pen:
                    break
                transform_vectors.append(axis_pen)
            else:
                break
        else:
            return [Vector3()]*3
        return transform_vectors

    # Axis must be a normalized/unit vector
    def test_axis(self, axis, min_a, max_a, min_b, max_b):
        l_dif = (max_b - min_a)
        r_dif = (max_a - min_b)
        if l_dif < 0 or r_dif < 0:
            return None
        overlap = l_dif if l_dif <= r_dif else -r_dif
        return axis*overlap
