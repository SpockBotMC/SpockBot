"""
MovementPlugin provides a centralized plugin for controlling all outgoing
position packets so the client doesn't try to pull itself in a dozen
directions.
Also provides very basic pathfinding
"""

import logging
import math

from spock.plugins.base import PluginBase
from spock.utils import pl_announce
from spock.vector import Vector3

logger = logging.getLogger('spock')


class MovementCore(object):
    def __init__(self):
        self.move_location = None

    def move_to(self, x, y, z):
        self.move_location = Vector3(x, y, z)


@pl_announce('Movement')
class MovementPlugin(PluginBase):
    requires = ('Net', 'Physics', 'ClientInfo')
    events = {
        'client_tick': 'client_tick',
        'action_tick': 'action_tick',
        'cl_position_update': 'handle_position_update',
        'phy_collision': 'handle_collision',
    }

    def __init__(self, ploader, settings):
        super(MovementPlugin, self).__init__(ploader, settings)

        self.movement = MovementCore()
        ploader.provides('Movement', self.movement)

    def client_tick(self, name, data):
        self.net.push_packet('PLAY>Player Position',
                             self.clientinfo.position.get_dict())

    def handle_position_update(self, name, data):
        self.net.push_packet('PLAY>Player Position and Look', data.get_dict())

    def handle_collision(self, name, data):
        if self.movement.move_location is not None:
            self.physics.jump()

    def action_tick(self, name, data):
        self.do_pathfinding()

    def do_pathfinding(self):
        move = self.movement
        clinfo = self.clientinfo
        if move.move_location is not None:
            if move.move_location.x == math.floor(clinfo.position.x) \
                    and move.move_location.z == math.floor(clinfo.position.z):
                move.move_location = None
            else:
                dx = move.move_location.x - clinfo.position.x
                dz = move.move_location.z - clinfo.position.z
                deg = 0
                if abs(dx) >= abs(dz):
                    # we should go along x
                    if dx > 0:
                        # go positive x
                        deg = 90
                    else:
                        # go neg x
                        deg = 270

                elif abs(dx) < abs(dz):
                    # we should go along z
                    if dz > 0:
                        # go positive z
                        deg = 0
                    else:
                        # go neg z
                        deg = 180

                self.physics.walk(deg)
