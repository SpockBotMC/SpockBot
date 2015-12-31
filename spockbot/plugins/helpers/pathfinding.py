"""
Very rough asychronous pathfinding plugin
Implements the Lazy Theta* pathfinding algorithm
"""

import collections

from spockbot.mcdata import blocks, constants as const
from spockbot.mcdata.utils import BoundingBox
from spockbot.plugins.base import PluginBase, pl_announce
from spockbot.plugins.tools.collision import(
    MTVTest, center_position, uncenter_position  # noqa
)
from spockbot.plugins.tools.event import EVENT_UNREGISTER
from spockbot.vector import Vector3


FOUND_VALID_PATH = 0x01
TIMEOUT_REACHED = 0x02
PATH_LIMIT_REACHED = 0x03
NO_VALID_PATH = 0x04


class PathfindingCore(object):
    def __init__(self, start_path):
        self.pathfind = start_path


class Path(object):
    def __init__(self, start_node, end_node):
        self.end_node = end_node
        self.open_list = [start_node]
        self.closed_list = []
        self.result = None

    def calc_f_val(self, node):
        return node.node_dist + self.end_node.dist(node)


class PathNode(Vector3):
    def __init__(self, *xyz):
        super(PathNode, self).__init__(*xyz)
        self.parent = None
        self.node_dist = 0
        self.is_fall = False
        self.is_jump = False

    def set(self, parent=None, is_fall=False, is_jump=False):
        self.parent = parent
        if parent:
            self.node_dist = parent.node_dist + self.dist(parent)
        else:
            self.node_dist = 0
        self.is_fall = is_fall
        self.is_jump = is_jump
        return self


@pl_announce('Pathfinding')
class PathfindingPlugin(PluginBase):
    requires = ('Event', 'World', 'Physics', 'ClientInfo', 'Timers')

    def __init__(self, ploader, settings):
        super(PathfindingPlugin, self).__init__(ploader, settings)

        self.bounding_box = BoundingBox(w=0.6, h=1.8)
        self.path_job = None
        self.col = MTVTest(
            self.world, BoundingBox(const.PLAYER_WIDTH, const.PLAYER_HEIGHT)
        )
        ploader.provides('Pathfinding', PathfindingCore(self.start_path))

    def build_list_from_node(self, node):
        ret = collections.deque()
        ret.append(node)
        while ret[0].parent is not None:
            ret.appendleft(ret[0].parent)
        return ret

    def start_path(self, pos, target, scb, fcb=None):
        pos = center_position(pos.floor(), BoundingBox(1, 1))
        target = center_position(target.floor(), BoundingBox(1, 1))
        new_job = Path(PathNode(pos), PathNode(target)), scb, fcb
        if self.path_job:
            self.path_job = new_job
            return
        self.path_job = new_job
        if not self.do_job():
            self.event.reg_event_handler('event_tick', self.do_job)

    def do_job(self, _=None, __=None):
        path, scb, fcb = self.path_job
        ret = self.pathfind(path)
        if ret == FOUND_VALID_PATH:
            self.path_job = None
            scb(self.build_list_from_node(path.result))
            return EVENT_UNREGISTER
        elif ret == NO_VALID_PATH and fcb:
            self.path_job = None
            fcb(None)

    def pathfind(self, path):
        while path.open_list and self.timers.get_timeout():
            cur_node = path.open_list.pop(0)
            p = cur_node.parent
            if p is not None and not (p.is_fall or p.is_jump):
                p = cur_node.parent.parent
                if p is not None and not (p.is_fall or p.is_jump) \
                        and self.raycast_bbox(p, cur_node):
                    cur_node.parent = p
                    cur_node.node_dist = p.node_dist + cur_node.dist(p)
            if cur_node == path.end_node:
                path.result = cur_node
                return FOUND_VALID_PATH
            for valid_node in self.find_valid_nodes(cur_node):
                if valid_node not in (path.open_list + path.closed_list):
                    path.open_list.append(valid_node)
            path.open_list.sort(key=path.calc_f_val)
            path.closed_list.append(cur_node)
        if not path.open_list and cur_node != path.end_node:
            return NO_VALID_PATH
        return TIMEOUT_REACHED

    def raycast_bbox(self, start, end):
        pos = PathNode(uncenter_position(start, self.col.bbox))
        path = end - start
        if not path:
            return True
        depth = Vector3(
            *map(lambda a: a[0] * a[1], zip(path.norm(), self.col.bbox))
        )
        i, r = divmod(path.dist(), depth.dist())
        for j in range(int(i)):
            pos += depth
            if not self.get_block(pos.floor() - Vector3(0, 1, 0)).bounding_box:
                return False
            if any(self.col.block_collision(pos)):
                return False
        return True

    def get_block(self, pos):
        return blocks.get_block(*self.world.get_block(*pos))

    def check_for_bbox(self, pos):
        pos = pos.floor()
        block = self.get_block(pos)
        if block.bounding_box:
            return True
        block = self.get_block(pos + Vector3(0, 1, 0))
        if block.bounding_box:
            return True
        return False

    def check_node(self, node, offset, node_list, walk_fall=True, jump=True):
        w_node = PathNode(node + offset).set(node)
        if walk_fall and not self.check_for_bbox(w_node):
            f_node = PathNode(w_node - Vector3(0, 1, 0)).set(node, True)
            if not self.check_for_bbox(f_node):
                node_list.append(f_node)
                walk_bool, fall_bool = False, True
            else:
                node_list.append(w_node)
                walk_bool, fall_bool = True, False
        else:
            walk_bool, fall_bool = False, False
        j_node = PathNode(w_node + Vector3(0, 1, 0)).set(node, is_jump=True)
        if jump and not walk_bool and not (node.is_fall or node.is_jump) \
                and not self.check_for_bbox(j_node):
                node_list.append(j_node)
                jump_bool = True
        else:
            jump_bool = False
        return walk_bool or fall_bool, jump_bool

    def find_valid_nodes(self, node):
        node_list = []
        pos_x, pos_jump_x = self.check_node(node, Vector3(1, 0, 0), node_list)
        pos_z, pos_jump_z = self.check_node(node, Vector3(0, 0, 1), node_list)
        neg_x, neg_jump_x = self.check_node(node, Vector3(-1, 0, 0), node_list)
        neg_z, neg_jump_z = self.check_node(node, Vector3(0, 0, -1), node_list)

        self.check_node(node, Vector3(1, 0, 1), node_list,
                        pos_x and pos_z, pos_jump_x and pos_jump_z)
        self.check_node(node, Vector3(-1, 0, -1), node_list,
                        neg_x and neg_z, neg_jump_x and neg_jump_z)
        self.check_node(node, Vector3(1, 0, -1), node_list,
                        pos_x and neg_z, pos_jump_x and neg_jump_z)
        self.check_node(node, Vector3(-1, 0, 1), node_list,
                        neg_x and pos_z, neg_jump_x and pos_jump_z)

        return node_list
