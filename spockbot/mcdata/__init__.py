from spockbot.mcdata import blocks
from spockbot.mcdata import items
from spockbot.mcdata.utils import find_by


def get_item_or_block(find, meta=0, init=True):
    ret = None
    if isinstance(find, int):  # by id
        ret = find_by(find, items.items, blocks.blocks)
    else:  # by name
        ret = find_by(find, items.items_name, blocks.blocks_name)
    if init and ret is not None:
        return ret(meta)
    return ret
