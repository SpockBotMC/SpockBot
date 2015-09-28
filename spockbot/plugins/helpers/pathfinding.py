import collections

from spock.plugins.base import PluginBase
from spock.plugins.tools import physics_tools
from spock.mcmap import mapdata
from spock.utils import pl_announce, BoundingBox
from spock.vector import Vector3

"""
Cross-product directional vector with bounding box to get increment length
increment and test for check_collision
repeat until end-node is reached
"""


class PathCore(object):
    def __init__(self, plug):
        self.plug = plug
        self.find_valid_nodes = plug.find_valid_nodes

    def pathfind(self, pos, target):
        pos = PathNode(pos).floor() + Vector3(0.5, 0, 0.5)
        target = PathNode(target).floor() + Vector3(0.5, 0, 0.5)
        return self.plug.pathfind(pos, target)

    def build_list_from_node(self, node):
        ret = collections.deque()
        ret.append(node)
        while ret[0].parent is not None:
            ret.appendleft(ret[0].parent)
        return ret

class PathNode(Vector3):
    def __init__(self, *xyz):
        super(PathNode, self).__init__(*xyz)
        self.parent = None
        self.child = None
        self.node_dist = 0
        self.is_jump = False
        self.is_fall = False

@pl_announce('Path')
class PathPlugin(PluginBase):
    requires = ('World', 'Physics', 'ClientInfo')

    def __init__(self, ploader, settings):
        super(PathPlugin, self).__init__(ploader, settings)

        self.bounding_box = BoundingBox(w=0.6, h=1.8)
        self.path = PathCore(self)
        self.col = physics_tools.MTVTest(self.world, self.bounding_box)
        ploader.provides('Path', self.path)

    def pathfind(self, start_node, end_node):
        def calc_f_val(node):
            return node.node_dist + end_node.dist(node)
        open_list = []
        closed_list = []
        open_list.append(start_node)
        while open_list:
            current_node = open_list.pop(0)
            if current_node.parent is not None:
                p = current_node.parent.parent
                if p is not None and self.raycast_bbox(p, current_node):
                    current_node.parent = p
                    current_node.node_dist = p.node_dist + current_node.dist(p)
            if current_node == end_node:
                return current_node
            for valid_node in self.find_valid_nodes(current_node)[0]:
                if valid_node not in (open_list + closed_list):
                    open_list.append(valid_node)
            open_list.sort(key=calc_f_val)
            closed_list.append(current_node)
        return None

    def raycast_bbox(self, start, end):
        pos = PathNode(start)
        pos.x -= self.col.bounding_box.w/2
        pos.z -= self.col.bounding_box.d/2
        path = end - start
        if not path:
            return True
        depth = Vector3(*map(lambda a: a[0] * a[1], zip(path.norm(), self.bounding_box)))
        i, r = divmod(path.dist(), depth.dist())
        for j in range(int(i)):
            pos += depth
            block_pos = pos.floor()
            block_id, meta = self.world.get_block(
                block_pos.x, block_pos.y-1, block_pos.z
            )
            block = mapdata.get_block(block_id, meta)
            if not block.bounding_box:
                return False
            t = self.col.block_collision(pos)
            if any(t):
                return False
        return True

    def find_valid_nodes(self, node):
        if not isinstance(node, PathNode):
            node = PathNode(node)
        block_node = PathNode(node.floor())
        walk_nodes = []
        jump_nodes = []
        fall_nodes = []
        test_positions = [block_node + Vector3(x, 0, 0) for x in (-1, 1)]
        test_positions.extend([block_node + Vector3(0, 0, z) for z in (-1, 1)])
        for block_pos in test_positions:
            player_pos = block_pos + Vector3(0.5, 0, 0.5)
            test = Vector3(player_pos)
            test.x -= self.col.bounding_box.w/2
            test.z -= self.col.bounding_box.d/2
            t = self.col.block_collision(test)
            if not any(t):
                fall_pos = player_pos - Vector3(0, 1, 0)
                test -= Vector3(0,1,0)
                t = self.col.block_collision(test - Vector3(0, 1, 0))
                if any(t):
                    player_pos.parent = node
                    player_pos.node_dist = node.node_dist + player_pos.dist(node)
                    walk_nodes.append(player_pos)
                else:
                    fall_pos.parent = node
                    fall_pos.node_dist = node.node_dist + fall_pos.dist(node)
                    fall_nodes.append(fall_pos)
                continue
            jump_pos = player_pos + Vector3(0, 1, 0)
            t = self.col.block_collision(test + Vector3(0, 1, 0))
            if not any(t):
                jump_pos.parent = node
                jump_pos.node_dist = node.node_dist + jump_pos.dist(node)
                jump_nodes.append(jump_pos)
        return walk_nodes, jump_nodes, fall_nodes
