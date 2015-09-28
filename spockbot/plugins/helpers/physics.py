"""
A Physics module built from clean-rooming the Notchian Minecraft client

Collision detection and resolution is done by a Separating Axis Theorem
implementation for concave shapes decomposed into Axis-Aligned Bounding Boxes.
This isn't totally equivalent to vanilla behavior, but it's faster and
Close Enough^TM

AKA this file does Minecraft physics
"""

import collections
import logging
import math

from spockbot.mcdata import blocks, constants as const
from spockbot.mcdata.utils import BoundingBox
from spockbot.plugins.base import PluginBase, pl_announce
from spockbot.plugins.tools import collision
from spockbot.vector import Vector3

logger = logging.getLogger('spockbot')

FP_MAGIC = 1e-4


class PhysicsCore(object):
    def __init__(self, pos, vec, abilities):
        self.pos = pos
        self.vec = vec
        self.sprinting = False
        self.move_accel = abilities.walking_speed
        self.abilities = abilities
        self.direction = Vector3()

    def jump(self):
        if self.pos.on_ground:
            if self.sprinting:
                ground_speed = Vector3(self.vec.x, 0, self.vec.z)
                if ground_speed:
                    self.vec += ground_speed.norm() * const.PHY_JMP_MUL
            self.vec.y = const.PHY_JMP_ABS

    def walk(self):
        self.sprinting = False
        self.move_accel = self.abilities.walking_speed

    def sprint(self):
        self.sprinting = True
        self.move_accel = self.abilities.walking_speed * const.PHY_SPR_MUL

    def move_target(self, vector):
        vector.y = self.pos.y
        if vector - self.pos < self.vec:
            self.pos.init(vector)
            self.vec.zero()
            return True
        else:
            self.direction = vector - self.pos

    def move_vector(self, vector):
        vector.y = 0
        self.direction = vector

    def move_angle(self, angle, radians=False):
        angle = angle if radians else math.radians(angle)
        self.direction = Vector3(math.sin(angle), 0, math.cos(angle))


@pl_announce('Physics')
class PhysicsPlugin(PluginBase):
    requires = ('Event', 'ClientInfo', 'World')
    events = {
        'physics_tick': 'tick',
        'client_position_update': 'stop_physics',
        'movement_position_reset': 'start_physics',
    }

    def __init__(self, ploader, settings):
        super(PhysicsPlugin, self).__init__(ploader, settings)
        self.vec = Vector3(0.0, 0.0, 0.0)
        bounding_box = BoundingBox(const.PLAYER_WIDTH, const.PLAYER_HEIGHT)
        self.col = collision.MTVTest(self.world, bounding_box)
        self.pos = self.clientinfo.position
        self.pause_physics = False
        self.pc = PhysicsCore(self.pos, self.vec, self.clientinfo.abilities)
        ploader.provides('Physics', self.pc)

    def stop_physics(self, _=None, __=None):
        self.vec.zero()
        self.pause_physics = True

    def start_physics(self, _=None, __=None):
        self.pause_physics = False
        self.event.reg_event_handler('physics_tick', self.tick)

    def tick(self, _, __):
        if self.pause_physics:
            return self.pause_physics
        self.apply_accel()
        mtv = self.get_mtv()
        self.apply_vector(mtv)
        self.pos.on_ground = mtv.y > 0
        self.vec -= Vector3(0, const.PHY_GAV_ACC, 0)
        self.apply_drag()
        self.pc.direction = Vector3()

    def get_block_slip(self):
        if self.pos.on_ground:
            block_pos = self.pos.floor()
            block_id, meta = self.world.get_block(
                block_pos.x, block_pos.y - 1, block_pos.z
            )
            return blocks.get_block(block_id, meta).slipperiness
        return 1

    def apply_accel(self):
        if not self.pc.direction:
            return
        if self.pos.on_ground:
            block_slip = self.get_block_slip()
            accel_mod = const.BASE_GND_SLIP**3 / block_slip**3
            accel = self.pc.move_accel * accel_mod * const.PHY_BASE_DRG
        else:
            accel = const.PHY_JMP_ACC
        self.vec += self.pc.direction.norm() * accel

    def apply_vector(self, mtv):
        self.pos += (self.vec + mtv)
        self.vec.x = 0 if mtv.x else self.vec.x
        self.vec.y = 0 if mtv.y else self.vec.y
        self.vec.z = 0 if mtv.z else self.vec.z

    def apply_drag(self):
        drag = self.get_block_slip() * const.PHY_DRG_MUL
        self.vec.x *= drag
        self.vec.z *= drag
        self.vec.y *= const.PHY_BASE_DRG

    # Breadth-first search for a minimum translation vector
    def get_mtv(self):
        pos = self.pos + self.vec
        pos = collision.uncenter_position(pos, self.col.bounding_box)
        q = collections.deque((Vector3(),))
        while q:
            current_vector = q.popleft()
            transform_vectors = self.col.check_collision(pos, current_vector)
            if not all(transform_vectors):
                break
            for vector in transform_vectors:
                test_vec = self.vec + current_vector + vector
                if test_vec.dist_sq() <= self.vec.dist_sq() + FP_MAGIC:
                    q.append(current_vector + vector)
        else:
            logger.warn('Physics failed to generate an MTV, bailing out')
            self.vec.zero()
            return Vector3()
        possible_mtv = [current_vector]
        while q:
            current_vector = q.popleft()
            transform_vectors = self.col.check_collision(pos, current_vector)
            if not all(transform_vectors):
                possible_mtv.append(current_vector)
        return min(possible_mtv)
