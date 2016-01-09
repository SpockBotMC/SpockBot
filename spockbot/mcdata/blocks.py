import sys

from minecraft_data.v1_8 import blocks_list

from spockbot.mcdata import constants as const, materials
from spockbot.mcdata.utils import BoundingBox
from spockbot.mcdata.utils import camel_case, find_by


blocks = {}
blocks_name = {}

# Used for extra logic outside of minecraft_data
_block_exts = {}


def get_block(block, meta=0, init=True):
    ret = None
    if isinstance(block, int):  # by id
        ret = find_by(block, blocks)
    else:  # by name
        ret = find_by(block, blocks_name)
    if init and ret is not None:
        return ret(meta)
    return ret


class Block(object):
    id = -1
    display_name = 'Block'
    name = 'block'
    hardness = 0.0
    stack_size = 0
    diggable = True
    bounding_box = None
    material = None
    slipperiness = 0.6
    harvest_tools = []
    variations = {}
    drops = []

    def __init__(self, meta=None):
        if meta is None:
            return
        self.metadata = meta
        # Set data off variations
        if self.metadata in self.variations:
            # TODO: apply other all possible variations
            self.display_name = self.variations[self.metadata]["display_name"]
        # Set data based off block extentions
        if self.id in _block_exts:
            _block_exts[self.id](self)

    def __str__(self):
        return '%s %i:%i' % (self.display_name, self.id,
                             getattr(self, 'metadata', 0))


def _convert_boundingbox(bb):
    if bb == 'block':
        return BoundingBox(1, 1)
    else:  # empty or unknown
        return None


def _make_block(block_dict):
    cls_name = '%sBlock' % camel_case(str(block_dict['name']))
    bases = (Block,)
    harvest_tools = []
    if "harvestTools" in block_dict:
        for tool in block_dict['harvestTools'].keys():
            harvest_tools.append(int(tool))
    variations = {}
    if "variations" in block_dict:
        for var in block_dict['variations']:
            variations[var['metadata']] = {"display_name": var['displayName']}
    mat = None
    if "material" in block_dict:
        mat = materials.get_material(block_dict['material'])
    bounding_box = _convert_boundingbox(block_dict['boundingBox'])
    attrs = {
        '__module__': sys.modules[__name__],
        'id': block_dict['id'],
        'display_name': block_dict['displayName'],
        'name': block_dict['name'],
        'hardness': block_dict['hardness'],
        'stack_size': block_dict['stackSize'],
        'diggable': block_dict['diggable'],
        'bounding_box': bounding_box,
        'material': mat,
        'harvest_tools': harvest_tools,
        'variations': variations,
        'drops': block_dict['drops'],
    }

    cls = type(cls_name, bases, attrs)
    assert not hasattr(sys.modules[__name__], cls_name), \
        'Block "%s" already registered at %s' % (cls_name, __name__)
    setattr(sys.modules[__name__], cls_name, cls)
    return cls


def _create_blocks():
    for block in blocks_list:
        cls = _make_block(block)
        blocks[cls.id] = cls
        blocks_name[cls.name] = cls

_create_blocks()


def block_ext(*block_ids):
    def inner(fn):
        for bid in block_ids:
            _block_exts[bid] = fn
        return fn

    return inner


@block_ext(85, 113, 188, 189, 190, 191, 192)
def _fence_ext(block):
    block.bounding_box = BoundingBox(1, 1.5)


@block_ext(107, 183, 184, 185, 186, 187)
def _gate_ext(block):
    block.direction = block.metadata & 0x03
    block.open = (block.metadata >> 2) & 0x01 == const.BLOCK_GATE_OPEN
    block.powered = block.metadata >> 3 == const.BLOCK_GATE_POWERED
    if block.open:
        block.bounding_box = None
    else:
        block.bounding_box = BoundingBox(1, 1.5)


@block_ext(64, 71, 193, 194, 195, 196, 197)
def _door_ext(block):
    block.section = (block.metadata >> 3) & 0x1
    if block.section == const.BLOCK_DOOR_LOWER:
        block.open = (block.metadata >> 2) & 0x01 == const.BLOCK_DOOR_OPEN
        block.direction = block.metadata & 0x03
        if not block.open:
            block.bounding_box = BoundingBox(1, 2)
        else:
            block.bounding_box = None
    elif block.section == const.BLOCK_DOOR_UPPER:
        block.hinge = block.metadata & 0x01
        block.bounding_box = None


@block_ext(44, 126, 182)
def _slab_ext(block):
    block.orientation = (block.metadata >> 3) & 0x1


@block_ext(96, 167)
def _trapdoor_ext(block):
    block.direction = block.metadata & 0x03
    block.open = (block.metadata >> 2) & 0x01 == const.BLOCK_TRAPDOOR_OPEN
    block.orientation = (block.metadata >> 3) & 0x1
    if block.open == const.BLOCK_TRAPDOOR_OPEN:
        block.bounding_box = None
    elif block.orientation == const.BLOCK_TRAPDOOR_UPPER:
        block.bounding_box = BoundingBox(1, 1)
    elif block.orientation == const.BLOCK_TRAPDOOR_LOWER:
        block.bounding_box = BoundingBox(1, 0.4)


@block_ext(111)
def _lillypad_ext(block):
    block.bounding_box = BoundingBox(1, 0.0, 1)
