from spock.mcmap import mapdata
from spock.vector import Vector3
from spock.mcdata import constants as const

UNIT_VECTORS = Vector3(1, 0, 0), Vector3(0, 1, 0), Vector3(0, 0, 1)

def gen_block_set(block_pos, xr=(-1, 2), yr=(0, 3), zr=(-1,2)):
    offsets = (
        (x, y, z)
        for x in range(*xr) for y in range(*yr) for z in range(*zr)
    )
    pos = block_pos.floor()
    return (pos + Vector3(*offset) for offset in offsets)


# Axis must be a normalized/unit vector
def check_axis(axis, min_a, max_a, min_b, max_b):
    l_dif = (max_b - min_a)
    r_dif = (max_a - min_b)
    if l_dif < 0 or r_dif < 0:
        return None
    overlap = l_dif if l_dif <= r_dif else -r_dif
    return axis*overlap


class MTVTest(object):
    def __init__(self, world, bounding_box):
        self.world = world
        self.bounding_box = bounding_box

    def check_collision(self, pos, vector):
        test_pos = pos + vector
        return self.block_collision(test_pos)

    def block_collision(self, pos):
        for block_pos in gen_block_set(pos):
            block_id, meta = self.world.get_block(
                block_pos.x, block_pos.y, block_pos.z
            )
            block = mapdata.get_block(block_id, meta)
            if not block.bounding_box:
                continue
            transform_vectors = []
            for i, axis in enumerate(UNIT_VECTORS):
                axis_pen = check_axis(
                    axis, pos[i], pos[i] + self.bounding_box[i],
                    block_pos[i], block_pos[i] + block.bounding_box[i]
                )
                if not axis_pen:
                    break
                transform_vectors.append(axis_pen)
            else:
                return transform_vectors
        return [Vector3()]*3
