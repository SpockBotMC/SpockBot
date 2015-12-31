"""
MovementPlugin provides a centralized plugin for controlling client
movement so the client doesn't try to pull itself in a dozen
directions.
"""

from spockbot.plugins.base import PluginBase, pl_announce
from spockbot.plugins.tools.event import EVENT_UNREGISTER
from spockbot.vector import Vector3


class MovementCore(object):
    def __init__(self, plug):
        self.__plug = plug
        self.move_to = plug.new_path

    def stop(self):
        self.__plug.path_nodes = None

    @property
    def is_moving(self):
        return self.__plug.path_nodes is not None

    @property
    def current_path(self):
        return self.__plug.path_nodes

    @property
    def current_target(self):
        p = self.current_path
        return p[0] if p else None

    @property
    def final_target(self):
        p = self.current_path
        return p[len(p)-1] if p else None


@pl_announce('Movement')
class MovementPlugin(PluginBase):
    requires = ('ClientInfo', 'Event', 'Net', 'Pathfinding', 'Physics')

    def __init__(self, ploader, settings):
        super(MovementPlugin, self).__init__(ploader, settings)
        self.movement = MovementCore(self)
        self.path_nodes = None
        ploader.provides('Movement', self.movement)

    def new_path(self, *xyz):
        target = Vector3(*xyz)
        self.pathfinding.pathfind(
            self.clientinfo.position, target, self.path_cb
        )

    def path_cb(self, result):
        self.path_nodes = result
        self.event.emit('movement_path_done')
        self.event.reg_event_handler('action_tick', self.follow_path)

    def follow_path(self, _, __):
        if not self.path_nodes:
            self.movement.stop()
            return EVENT_UNREGISTER
        target = self.path_nodes[0]
        jumped = False
        if target.is_jump and self.clientinfo.position.on_ground:
            self.physics.jump()
            jumped = True
        if self.physics.move_target(target) or jumped:
            self.path_nodes.popleft()
            if not self.path_nodes:
                self.movement.stop()
