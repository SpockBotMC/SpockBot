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

    def stop(self):
        self.move_location = None

    def is_moving(self):
        return self.move_location is not None

@pl_announce('Movement')
class MovementPlugin(PluginBase):
    requires = ('Net', 'Physics', 'ClientInfo', 'Event')
    events = {
        'client_tick': 'client_tick',
        'action_tick': 'action_tick',
        'client_position_update': 'handle_position_update',
        'physics_collision': 'handle_collision',
        'client_join_game': 'handle_join_game',
    }

    def __init__(self, ploader, settings):
        super(MovementPlugin, self).__init__(ploader, settings)

        self.flag_pos_reset = False
        self.movement = MovementCore()
        self.connected_to_server = False
        ploader.provides('Movement', self.movement)

    def client_tick(self, name, data):
        if not self.connected_to_server:
            return
        self.net.push_packet('PLAY>Player Position and Look',
                             self.clientinfo.position.get_dict())
        if self.flag_pos_reset:
            self.event.emit('movement_position_reset')
            self.flag_pos_reset = False

    def handle_join_game(self, name, data):
        self.connected_to_server = True

    def handle_position_update(self, name, data):
        self.flag_pos_reset = True

    def handle_collision(self, name, data):
        if self.movement.move_location is not None:
            self.physics.jump()

    def action_tick(self, name, data):
        self.do_pathfinding()

    def do_pathfinding(self):
        move = self.movement
        clinfo = self.clientinfo
        if move.move_location is not None:
            if round(move.move_location.x, 2) == round(clinfo.position.x, 2) \
                    and round(move.move_location.z, 2) == round(clinfo.position.z, 2):
                move.stop()
            else:
                self.physics.move_target(move.move_location)
                self.physics.walk()
