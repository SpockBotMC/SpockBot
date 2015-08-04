"""
MovementPlugin provides a centralized plugin for controlling all outgoing
position packets so the client doesn't try to pull itself in a dozen directions.
Also provides very basic pathfinding
"""

from spock.utils import pl_announce
from spock.mcp import mcdata
from spock.utils import Position
from spock.plugins.base import PluginBase
import math

import logging
logger = logging.getLogger('spock')

class MovementCore:
    def __init__(self):
        self.move_location = None
    def move_to(self, x, y, z):
        self.move_location = Position(x, y, z)

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
        super(self.__class__, self).__init__(ploader, settings)

        self.movement = MovementCore()
        ploader.provides('Movement', self.movement)

    def client_tick(self, name, data):
        self.net.push_packet('PLAY>Player Position', self.clientinfo.position.get_dict())

    def handle_position_update(self, name, data):
        self.net.push_packet('PLAY>Player Position and Look', data.get_dict())

    def handle_collision(self, name, data):
        if self.movement.move_location != None:
            self.physics.jump()

    def action_tick(self, name, data):
        self.do_pathfinding()

    def do_pathfinding(self):
        if self.movement.move_location != None:
            if self.movement.move_location.x == math.floor(self.clientinfo.position.x) and self.movement.move_location.z == math.floor(self.clientinfo.position.z):
                self.movement.move_location = None;
            else:
                dx = self.movement.move_location.x - self.clientinfo.position.x
                dz = self.movement.move_location.z - self.clientinfo.position.z
                deg = 0
                if abs(dx) >= abs(dz):
                    #we should go along x
                    if dx > 0:
                        #go positive x
                        deg = 90
                    else:
                        #go neg x
                        deg = 270

                elif abs(dx) < abs(dz):
                    #we should go along z
                    if dz > 0:
                        #go positive z
                        deg = 0
                    else:
                        #go neg z
                        deg = 180

                self.physics.walk(deg)
