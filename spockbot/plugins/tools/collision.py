from spockbot.mcdata import blocks
from spockbot.vector import Vector3

UNIT_VECTORS = Vector3(1, 0, 0), Vector3(0, 1, 0), Vector3(0, 0, 1)


def center_position(pos, bbox):
    return Vector3(pos.x + bbox.w/2.0, pos.y, pos.z + bbox.d/2.0)


def uncenter_position(pos, bbox):
    return Vector3(pos.x - bbox.w/2.0, pos.y, pos.z - bbox.d/2.0)


def gen_block_set(block_pos, xr=(-1, 2), yr=(0, 3), zr=(-1, 2)):
    pos = block_pos.floor()
    return (
        pos + Vector3(x, y, z)
        for x in range(*xr) for y in range(*yr) for z in range(*zr)
    )


# Axis must be a normalized/unit vector
def check_axis(axis, min_a, max_a, min_b, max_b):
    l_dif = (max_b - min_a)
    r_dif = (max_a - min_b)
    if l_dif < 0 or r_dif < 0:
        return None
    overlap = l_dif if l_dif <= r_dif else -r_dif
    return axis*overlap


# Terribly named class with terribly named methods mostly useful to physics
# implementations, rarely useful to other things. Much too clever for its own
# good but reasonably fast for it.
class MTVTest(object):
    def __init__(self, world, bbox):
        self.world = world
        self.bbox = bbox

    def check_collision(self, pos, vector):
        test_pos = pos + vector
        return self.block_collision(test_pos)

    def block_collision(self, pos):
        # This line is confusing. Basically it figures out how many block
        # coordinates the bounding box currently occupies. It's not clear what
        # "b" stands for so take your pick: Blocks, Bounds, how-Big-is-the-Box
        b = (pos + self.bbox).ceil() - pos.floor()
        for block_pos in gen_block_set(pos, *zip((0, -1, 0), b)):
            block = blocks.get_block(*self.world.get_block(*block_pos))
            if not block.bounding_box:
                continue
            transform_vectors = []
            for i, axis in enumerate(UNIT_VECTORS):
                axis_pen = check_axis(
                    axis, pos[i], pos[i] + self.bbox[i],
                    block_pos[i], block_pos[i] + block.bounding_box[i]
                )
                if not axis_pen:
                    break
                transform_vectors.append(axis_pen)
            else:
                return transform_vectors
        return [Vector3()]*3
